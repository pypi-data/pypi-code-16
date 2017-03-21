from django.conf import settings
from main.models import Auth_csv
from main.models import Profile
from main.models import Department
from main.models import Usr
import os,csv



CSV_CONNECTION =settings.SMIT_CONFIG["csv_connection"]

def inject_csv(path_to_csv):

    file = open(path_to_csv, 'rb')
    user_reader = csv.reader(file, delimiter=';')
    for row in user_reader:      
        try:
            user = Auth_csv.objects.get(email=row[0])
            pass
        except Auth_csv.DoesNotExist :
            user = Auth_csv(email=row[0],
                        password=row[1])
            user.save()
  
        profile = Profile.objects.get(profDesignation=row[2])
        department = Department.objects.get(depDesignation="informatique")

        try : 
            smitUser=Usr.objects.get(userEmail=row[0])
            print "user exist in usr"
            pass
        except Usr.DoesNotExist:
            smitUser= Usr(userEmail=row[0],
                  userName=row[0],
                  department=department,
                  profile=profile)
            smitUser.save()
            print "user ", row[0] ,"created"


def clean_up():
    Auth_csv.objects.all().delete()



def write_user_file(csv_file,pst_full_path):
    destination = open(pst_full_path, 'w')
    for chunk in csv_file.chunks():
        destination.write(chunk)
    destination.close()


def csvAuthentification(email,password):
    result = {
        'userEmail':"",
        'userName':"",
        'department':"informatique"
        }
    try:
        smitUser = Auth_csv.objects.get(email=email,password=password)
        print "user auth ok"
        result["userEmail"]=email
        result["userName"]=email
        return result

    except Auth_csv.DoesNotExist:
        print "user", email," does not exist"
        return -5



def launch_injection(csv_file):
    write_user_file(csv_file,CSV_CONNECTION["file_path"])
    inject_csv(CSV_CONNECTION["file_path"])

