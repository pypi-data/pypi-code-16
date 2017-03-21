import os,time
from django.conf import settings
import sys
import socket
from main.models import SmitTask

def convertToUtf8(filename):
    #possible encodings
    encodings = ('iso-8859-1','windows-1253', 'iso-8859-7', 'macgreek')

    # try to open the file and exit if some IOError occurs
    try:
        f = open(filename, 'r').read()
    except Exception:
        sys.exit(1)

    for enc in encodings:
        try:

            data = f.decode(enc)
            break
        except Exception:

            if enc == encodings[-1]:
                sys.exit(1)
            continue


    return data.encode('utf-8')



def getSession(request,param=None):
    if param in request.session:
        return request.session[param]


def handle_uploaded_file(f):
    #send the file to the web site temp folder
    temp_destination= os.path.join(settings.MEDIA_ROOT, 'temp', f.name)
    temp_handler = open(temp_destination, 'wb+')
    for chunk in f.chunks():
        temp_handler.write(chunk)
    temp_handler.close()
    # we must encode this file, so on data can be read by Template object
    # this is not optimized yet; because we write the file and after that we convert it, it might be better if we do both actions in one trnasaction
    #write the utf-8 log in logs folder
    print "in upload"
    destination= os.path.join(settings.MEDIA_ROOT, 'logs', f.name)
    handler= open(destination, 'wb+')
    handler.write(convertToUtf8(temp_destination))
    handler.close()
    #delete the temp file
    os.remove(temp_destination)

def cancel(task_id):
    from celery.task.control import revoke
#    from carrot.connection import DjangoBrokerConnection
#    c = DjangoBrokerConnection()
    if task_id:
        revoke(task_id)


def removeLogs():
    for root, dirs, files in os.walk(os.path.join(settings.MEDIA_ROOT, 'logs')):
        for f in files:
            os.unlink(os.path.join(root, f))



def getLog(file_name=None):
    if file_name:
        destination= os.path.join(settings.MEDIA_ROOT, 'logs',file_name)
        try:
            filehandler=open(destination,'r')
            log_content = ""
            for line in filehandler:
#                print line
                log_content+=line
        except Exception,e:
            print e
            return None

        return log_content

    else :
        return None




def check_port(hostname,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(port)
    try: 
        s.connect((hostname, port))
        print "connection ok for %s" % hostname
        return True
    except socket.error as e:
        print "Error on connect: %s" % e
        s.close()
        return False


def check_icmp(hostname):
    response = os.system("ping -c 1 " + hostname)
    if response == 0:
        print hostname, 'is up!'
        return True
    else:
        print hostname, 'is down'
        return False



def is_path_exist(path):
    try:
        output = subprocess.check_output(['ls',path])
        return True
    except:
        print "error"
        return False



def get_check_network():

    ZIMBRA = settings.SMIT_CONFIG["zimbra"]
    DEFAULT = settings.SMIT_CONFIG["default"] 
    IMAP_SRC = settings.SMIT_CONFIG["imapsync_src"]
    IMAP_DST = settings.SMIT_CONFIG["imapsync_dst"]
    PST = settings.SMIT_CONFIG["pst_migration"]
    CSV_CONNECT = settings.SMIT_CONFIG["csv_connection"]

    zimbra_check = {  'TESTING ICMP  ': check_icmp(ZIMBRA["zimbra-server"]),
                      'TESTING WEB ACCESS' : check_port(ZIMBRA["zimbra-server"],ZIMBRA["zimbra-port"]),
                      'TESTING ADMIN WEB ACCESS' : check_port(ZIMBRA["zimbra-server"],ZIMBRA["zimbra-admin-port"]),
                      'TESTING IMAP ACCESS' : check_port(ZIMBRA["zimbra-server"],DEFAULT["imap"]),
                      'TESTING IMAPS ACCES': check_port(ZIMBRA["zimbra-server"],DEFAULT["imaps"]),
                      'TESTING LDAP PORT' : check_port(ZIMBRA["zimbra-server"],DEFAULT["ldap"])
    }
    imap_src_check  = { 'TESTING ICMP' : check_icmp(IMAP_SRC["host1"]),
                        'TESTING IMAP ACCESS' : check_port(IMAP_SRC["host1"],IMAP_SRC["port"]),
                        'TESTING IMAPS ACCES': check_port(IMAP_SRC["host1"],IMAP_SRC["port-ssl"])
    }

    imap_dst_check  = { 'TESTING ICMP' : check_icmp(IMAP_DST["host2"]),
                        'TESTING IMAP ACCESS' : check_port(IMAP_DST["host2"],IMAP_DST["port"]),
                        'TESTING IMAPS ACCES': check_port(IMAP_DST["host2"],IMAP_DST["port-ssl"])
    }
    
    file_check = {     'TESTING CSV FILES' : is_path_exist(CSV_CONNECT["file_path"]),
                        'TESTING MOUTIING PATH' : is_path_exist(PST["path_to_pst"]) 

    }
    
    return zimbra_check,imap_src_check,imap_dst_check,file_check
    
def clean_smit_task():
    SmitTask.objects.all().delete()

