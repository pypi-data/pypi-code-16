#!/usr/local/bin/python
# coding: utf-8
import os

from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
import datetime
from django.shortcuts import render_to_response
from main.forms import SearchForm
from main.forms import ConnectionForm
from main.forms import FileUpload
from main.forms import EditProfile
from main.forms import Tools
from main.forms import QuickSearch
from main.system_functions import getSession
from main.system_functions import removeLogs
from main.system_functions import handle_uploaded_file
from main.system_functions import cancel
from main.system_functions import getLog
from main.ldap_authentification import ldapAuthentification
from main.system_functions import clean_smit_task
from django.conf import settings

from main.models import SmitTask
from main.models import CeleryTaskmeta
from main.models import UserManager
from main.models import Usr
from main.models import Department
from main.models import Profile
from main.models import TaskType



from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q
import json
from django.conf import settings

from main.system_functions import get_check_network
from main.csv_authentification import launch_injection
from main.csv_authentification import csvAuthentification
from django.core.paginator import Paginator, EmptyPage
#from django.template import Context, Template
#from django.core.servers.basehttp import FileWrapper
#import mimetypes
#from django.core.context_processors import request




NB_LIGNE_PAR_PAGE=50
connection_type = settings.SMIT_CONFIG["global"]["connection_type"]


#def csrf_failure(request, reason=""):
 #   ctx = {'message': 'some custom messages'}
  #  return render(main.templates.index, ctx)

@csrf_protect
def logout(request):
        try:
            request.session.clear()
            #print "deleted session" + request.session['userEmail']
        except KeyError:
            pass
        return HttpResponseRedirect("/index/")

@csrf_protect
def index(request):
    session=getSession(request,'userEmail')
    print session
    error='test'
    if not session:
        if request.method == 'POST': # If the form has been submitted...
            print "in post data"
            form = ConnectionForm(request.POST) # A form bound to the POST data
            if form.is_valid(): # All validation rules pass
                email = form.cleaned_data["email"]
                password = form.cleaned_data["password"]
                print "email = ", email 
                print " password ", password
                if connection_type == 'ldap':
                    print "connecting via ldap -- "
                    authentication_result=ldapAuthentification(email,password)
                else:
                    print "connecting via ", connection_type
                    authentication_result=csvAuthentification(email,password)
                try:
                    user_email=authentication_result["userEmail"]
                    print "****",user_email,"Ldap Ok"
                    try:
                        smitUser = Usr.objects.get(userEmail=email)
                        print "User OK"

                    except Usr.DoesNotExist:
                        print "User does not exist"
                        ldapDepartment= authentication_result["department"]

                        try:
                            if not ldapDepartment:
                                print "dep is null, w'll use the default one"
                                ldapDepartment ="default"
                            department = Department.objects.get(depDesignation=ldapDepartment)
                        except Department.DoesNotExist:
                            print "Department does not exist"
                            department = Department(depDesignation=ldapDepartment)
                            department.save()
                            print "Department created"

                        profile = Profile.objects.get(profDesignation="default")
                        smitUser= Usr(userEmail=user_email,
                                          userName=authentication_result["userName"],
                                          department=department,
                                          profile=profile
                                          )
                        smitUser.save()
                        print "user created"
                    request.session['userEmail'] = user_email

                    if smitUser.isAdmin == True:
                        return render(request,'index_admin.html',{'session':user_email,})
                    else:
                        #accessible_task_types = TaskType.objects.filter(profile__profId = Usr.objects.get(userEmail=user_email).profile.profId)
                        return render(request,'index_user.html',{'session':user_email,})

                except TypeError:
                    print "LDAP not Ok"

                    if authentication_result == -2:
                        error = "An Error was occurred when trying to connect, please try later !"
                    elif authentication_result ==-1:
                        error = "Invalid Password, please try again !"
                    elif authentication_result == 0:
                        error = "This Email is not registered in our LDAP database, please use your real office Email !"

                    return render(request,'connection.html', {'form': form,'error':error})


        else:
            form = ConnectionForm() # An unbound form
        return render(request,'connection.html', {'form': form,})
    else:
        user = Usr.objects.get(userEmail=session)
        if user.isAdmin:
            return render(request,'index_admin.html',{'session':session,})
        else:
#            accessible_task_types = TaskType.objects.filter(profile__profId = Usr.objects.get(userEmail=session).profile.profId)
            return render(request,'index_user.html',{'session':session,})





#def migrateUserData(request):
#    session=getSession(request,'userEmail')
#    if session:
#        accessible_task_types = TaskType.objects.filter(profile__profId = Usr.objects.get(userEmail=session).profile.profId)
#        return render('index_user.html',{'session':session,'taskTypes':accessible_task_types,})
#
@csrf_protect
def showSmitStatistics(request):
    #c_ veut dire critere
    # get the session
    session=getSession(request,'userEmail')

    if session:
        user = Usr.objects.get(userEmail=session)
        if (user.isAdmin == True):
	    searchForm = QuickSearch()
            manager = UserManager.objects.get(usr=Usr.objects.get(userEmail=session))
            managed_users = Usr.objects.filter(department__depId__in = [dpt.depId for dpt in manager.managedDepartments.all()])
            key_word=request.GET.get('key_word')
            if (key_word):
                taches_list = SmitTask.objects.filter(Q(taskId__icontains=key_word) |
                                                      Q(smitStatus__icontains=key_word) |
                                                      Q(smitWorkerName__icontains=key_word) |
                                                      Q(smitResult__icontains=key_word) |
                                                      Q(smitConcernedEmail__icontains=key_word)|
                                                      Q(smitTasksBatch__icontains=key_word)|
                                                      Q(usr__userName__icontains=key_word) |
                                                      Q(taskType__taskTypeDesignation__icontains=key_word)
                                                      #Q(smit_log_file__contains=key_word)
                                                      ).filter(usr__userId__in=[usr.userId for usr in managed_users])

            else:
                taches_list = SmitTask.objects.all()
            paginator = Paginator(taches_list, NB_LIGNE_PAR_PAGE)
            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1
            # If page request (9999) is out of range, deliver last page of results.
            try:
                taches = paginator.page(page)
            except (EmptyPage, InvalidPage):
                taches = paginator.page(paginator.num_pages)

            if key_word == None:
                key_word = ''
            nbrows = taches_list.__len__()
            return render(request,'smit_statistics.html',{'taches':taches,'session':session,'key_word':key_word,'nb_results':nbrows,'searchForm':searchForm,})

    else :
        return HttpResponseRedirect('/logout/')


def myResult(request):
    session=getSession(request,'userEmail')
    if session:
        taches = SmitTask.objects.filter(Q(usr__userEmail=session)|Q(smitConcernedEmail=session))
        return render(request,'user_statistics.html',{'taches':taches,'session':session,})

@csrf_protect
def editUserProfile(request):
    session=getSession(request,'userEmail')
    error=''
    status='OK'
    if session:
        user = Usr.objects.get(userEmail=session)
        if (user.isAdmin == True):
            if request.method == 'POST':
                userEmail=request.POST.get('userEmail')
                form = EditProfile(request.POST)
                if form.is_valid():
                    try:
                        profile = Profile.objects.get(profDesignation=form.cleaned_data["user_profile"])
                        user = Usr.objects.get(userEmail=userEmail)
                        user.profile=profile
                        user.save()
                    except Exception,e:
                        error= e.value
                        status= 'KO'
                    server_response={"status":status,"error":error}
                    return HttpResponse(json.dumps(server_response),mimetype='application/javascript')
            else:
                userEmail=request.GET.get('userEmail')
                form = EditProfile()

            return render(request,'edit_profile.html', {'form': form,'userEmail':userEmail})
    else:
        return HttpResponseRedirect('/logout/')

@csrf_protect
def showCeleryStatistics(request):
   # taches = CeleryTaskmeta.objects.all()
    session=getSession(request,'userEmail')
    if session:
        user = Usr.objects.get(userEmail=session)
        if (user.isAdmin == True):
	    searchForm = SearchForm()
            taches_list = CeleryTaskmeta.objects.all()
            nbrows = taches_list.__len__()
            #tache = cache.get('task_id')
            paginator = Paginator(taches_list, NB_LIGNE_PAR_PAGE)
            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1
            # If page request (9999) is out of range, deliver last page of results.
            try:
                taches = paginator.page(page)
            except (EmptyPage, InvalidPage):
                taches = paginator.page(paginator.num_pages)
            return render(request,'celery_statistics.html',{'taches':taches,'session':session,'searchForm':searchForm,})
    else:
        return HttpResponseRedirect('/logout/')
@csrf_protect
def search(request):
    session=getSession(request,'userEmail')
    if session:
        user = Usr.objects.get(userEmail=session)
        if (user.isAdmin == True):
            if request.method == 'POST': # If the form has been submitted...
                form = SearchForm(request.POST) # A form bound to the POST data
                if form.is_valid(): # All validation rules pass

                    filters={}

                    if form.cleaned_data['task_result']:
                        filters['smitResult__icontains']=form.cleaned_data['task_result']
                    if form.cleaned_data['task_status']:
                        filters['smitStatus__icontains']=form.cleaned_data['task_status']
                    if form.cleaned_data['task_type']:
                        filters['taskType__taskTypeDesignation__icontains']=form.cleaned_data['task_type']
                    if form.cleaned_data['task_start_date']:
                        filters['smitStartDate__gte']=form.cleaned_data['task_start_date']
                    if form.cleaned_data['task_end_date']:
                        filters['smitEndDate__lte']=form.cleaned_data['task_end_date']
		    if form.cleaned_data['concerned_user']:
                        filters['smitConcernedEmail__icontains']=form.cleaned_data['concerned_user']
	
                    taches_list= SmitTask.objects.filter(**filters)
                    # il y a un bug par rapport a la requete post, pour l'instant pas de pagination ! ou une seule page contenant le tout
                    paginator = Paginator(taches_list, 900)
                    try:
                        page = int(request.GET.get('page', '1'))
                    except ValueError:
                        page = 1
                    # If page request (9999) is out of range, deliver last page of results.
                    try:
                        taches = paginator.page(page)
                    except (EmptyPage, InvalidPage):
                        taches = paginator.page(paginator.num_pages)
                    nbrows = taches.__len__()
		    searchForm = QuickSearch()
                    return render(request,'smit_statistics.html', {'taches':taches,'session':session,'nb_results':nbrows,'searchForm':QuickSearch,}) # Redirect after POST
                    #return HttpResponseRedirect('/smitAdmin/showResults/')

            else:
                form = SearchForm() # An unbound form

            return render(request,'search_form.html', {'form': form,'session':session,})
    else:
         return HttpResponseRedirect('/logout/')
@csrf_protect
def getListUsers(request):
    session=getSession(request,'userEmail')
    if session:
        user = Usr.objects.get(userEmail=session)
        if (user.isAdmin == True):
            manager = UserManager.objects.get(usr=Usr.objects.get(userEmail=session))
            managed_users = Usr.objects.filter(department__depId__in = [dpt.depId for dpt in manager.managedDepartments.all()])
            key_word=request.GET.get('key_word')
            if (key_word):
                users_list = managed_users.filter(Q(userName__icontains=key_word) |
                                                      Q(userEmail__icontains=key_word) |
                                                      Q(department__depDesignation__icontains=key_word) |
                                                      Q(profile__profDesignation__icontains=key_word)

                                                      ).exclude(userEmail__exact=session)
            else:

                users_list = managed_users.all().exclude(userEmail__exact=session)

            paginator = Paginator(users_list, NB_LIGNE_PAR_PAGE)
            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1
            # If page request (9999) is out of range, deliver last page of results.
            try:
                users = paginator.page(page)
            except (EmptyPage, InvalidPage):
                users = paginator.page(paginator.num_pages)

            if key_word == None:
                key_word = ''
            nbrows = users_list.__len__()
            return render(request,'list_users.html',{'users':users,'session':session,'key_word':key_word,'nb_results':nbrows,})

    else :
        return HttpResponseRedirect('/logout/')

@csrf_protect
def showLog(request):
    session=getSession(request,'userEmail')
    if session:
        user = Usr.objects.get(userEmail=session)
        if (user.isAdmin == True):
            file_name = request.GET.get('file_name')
            log_content = getLog(file_name)
            return render(request,'log.html', {'log':log_content,})
    else :
        return HttpResponseRedirect('/logout/')

@csrf_protect
def upload_file(request):
    if request.method == 'POST': # If the form has been submitted...
        form = FileUpload(request.POST,request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            print request.FILES['file'].name
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/') # Redirect after POST
    else:
        form = FileUpload() # An unbound form

    return render(request,'upload.html', {'form': form,})
@csrf_protect
def sousTest(request):
    print "sousTest"
    #return HttpResponseRedirect('/logout/')


@csrf_protect
def runApplications(request):
    session=getSession(request,'userEmail')
    if session :
        user = Usr.objects.get(userEmail=session)
        list_applications = list(settings.NEW_APPLICATIONS)
        if (user.isAdmin == True):
            return render(request,'main_run_applications_admin.html', {'session':session,'list_applications': list_applications,})
        else:
            accessible_applications = TaskType.objects.filter(profile__profId = Usr.objects.get(userEmail=session).profile.profId)
            return render(request,'main_run_applications_user.html', {'session':session,'accessible_task_types':accessible_applications})

    else:
        return HttpResponseRedirect('/logout/')




@csrf_protect
def checkNetwork(request):
    session=getSession(request,'userEmail')
    if session :
        zimbra_check,imap_src,imap_dst,file_check = get_check_network()    
        user = Usr.objects.get(userEmail=session)
        if (user.isAdmin == True):
           return render(request,'check_network_admin.html', {'session':session,'zimbra_check': zimbra_check, 'imap_src':imap_src,'imap_dst':imap_dst, 'file_check':file_check})
    else:
        return HttpResponseRedirect('/logout/')


@csrf_protect
def tools(request):
    session=getSession(request,'userEmail')
    user = Usr.objects.get(userEmail=session)
    form = Tools()
    if session :
        if request.method == 'POST':
            if request.POST['formType'] == "importCSV":
                launch_injection(request.FILES['file'])
                return render(request,'tools.html', {'session':session,'form':form})
	    if request.POST['formType'] == "cleanTask":
		clean_smit_task()
		return render(request,'tools.html', {'session':session,'form':form})
        if (user.isAdmin == True):
            return render(request,'tools.html', {'session':session,'form':form})
    else:
        return HttpResponseRedirect('/logout/')
                    

@csrf_protect
def deleteAll(request):
    session=getSession(request,'userEmail')
    if session:
        user = Usr.objects.get(userEmail=session)
        if (user.isAdmin == True):
            SmitTask.objects.all().delete()
#            CeleryTaskmeta.objects.all().delete()
            removeLogs()
            return HttpResponseRedirect('/logout/')
    else:
        return HttpResponseRedirect('/logout/')

@csrf_protect
def cancelListTasks(request):
    session=getSession(request,'userEmail')
    if session:
        user = Usr.objects.get(userEmail=session)
        if (user.isAdmin == True):
            list_tasks = request.POST.getlist('checked_checkbox')
            for task_id in list_tasks:
                smit = SmitTask.objects.get(taskId=task_id)
                if (smit.smitStatus == 'Sent to queue'):
                    cancel(task_id)
                    smit = SmitTask.objects.get(taskId=task_id)
                    smit.smitStatus='Canceled'
                    smit.smitResult='Canceled'
                    smit.smitEndDate=datetime.datetime.now()
                    smit.save()
            return HttpResponseRedirect('/smitAdmin/showResults/')
    else:
        return render(request,'/logout/')

##################not used#######################################################
#cancelListTasks can take one task in the list
@csrf_protect
def cancelTask(request):

    task_id=request.GET.get('taskId')
    smit = SmitTask.objects.get(taskId=task_id)
    if (smit.smitStatus == 'Sent to queue'):
        cancel(task_id)
        smit = SmitTask.objects.get(taskId=task_id)
        smit.smitStatus='Canceled'
        smit.smitResult='Canceled'
        smit.smitEndDate=datetime.datetime.now()
        smit.save()

    else:
        pass
        #il faut ajouter un message d'erreur comme quoi la tache elle est deja partie au worker

    return HttpResponseRedirect('/smitAdmin/showResults/')
######################################################################################
