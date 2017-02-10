from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import json
from django.views.decorators.csrf import csrf_exempt
from .models import *

# Create your views here.
def index(request):
    return render(request, 'django_assistant/index.html', {})


def decode_dict(dict1):
    keys = dict1.keys()
    for key in keys:
	print "key is",key
	print "value is",dict1[key]
	if type(dict1[key]) == dict:
	    decode_dict(dict1[key])
    return ""

@csrf_exempt
def a_create_api(request):
    #~ import ipdb;ipdb.set_trace()
    edit_mode = request.POST.get("edit_mode",None)
    api_id = request.POST.get("api_id",None)
    url = request.POST.get("url",None)
    params = request.POST.get("params",None)
    desc = request.POST.get("desc",'')
    http_type = request.POST.get("http_type",None)
    
    if edit_mode == "add":
	api = Api()
	

    if edit_mode == "edit":
	api = Api.objects.get(id=api_id)
    
    api.url = url
    api.desc = desc
    api.http_type = http_type
    api.save()

    
    dict1 = {}
    dict1["result"] = "Success"
    return HttpResponse(json.dumps(dict1),content_type="application/json")

@csrf_exempt
def a_edit_params(request):
    edit_mode = request.POST.get("edit_mode",None)
    params = eval(request.POST.get("params",None))
    api_id = request.POST.get("api_id",None)
    print request.POST
    api = Api.objects.get(id=api_id)
    if edit_mode == "add":
	if params:
	    param = ApiParam()
	    param.params = params
	    param.save()
	    api.params.add(param)
    
    dict1 = {}
    dict1["result"] = "Success"
    return HttpResponse(dict1,content_type="application/json")

@csrf_exempt
def a_get_apis(request):
   
    list1 = []
    
    for api in Api.objects.all():
	list2 = []
	dict2 = {}
	dict2["api_id"] = api.id
	dict2["url"] = api.url
	dict2["params"] = api.get_params()	    
	dict2["http_type"] = api.http_type
	list1.append(dict2)
    
    dict1={}
    dict1["result"] = "Success"
    dict1["response"] = list1
    return HttpResponse(json.dumps(dict1),content_type="application/json")

@csrf_exempt
def a_fetch_api_details(request):
    api_id = request.POST.get("api_id",None)
    
    
    api = Api.objects.get(id=api_id)
    api_dict = {}
    api_dict["id"] = api.id
    api_dict["url"] = api.url
    api_dict["params"] = api.get_params()
    api_dict["http_type"] = api.http_type
    api_dict["descr"] = api.desc
    
    
    dict1 = {}
    dict1["api"] = api_dict
    dict1["result"] = "Success"
    return HttpResponse(json.dumps(dict1),content_type="aplication/json")


@csrf_exempt
def a_delete_api(request):
    api_id = request.POST.get("api_id",None)
    api = Api.objects.get(id=api_id)
    for param in api.params.all():
	param.delete()
    
    api.delete()
    
    dict1 = {}
    dict1["result"] = "Success"
    return HttpResponse(json.dumps(dict1),content_type="application/json")


@csrf_exempt
def a_trial_api(request):
    print request.POST.get("var")
    dict1 = {}
    dict1["sample"] = [{"name":"jerin","age":"25"},{"name":"jerin2","age":"26"}]
    return HttpResponse(json.dumps(dict1),content_type="aplication/json")








