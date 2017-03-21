from django import forms
import os,time

from main.models import  TaskType
from main.models import Profile
from main.models import UserManager
from main.models import Usr
from django.contrib.admin import widgets


class FileUpload(forms.Form):
    file  = forms.FileField()


    
    
class ConnectionForm(forms.Form):
    email = forms.EmailField(label = 'Email' )
    password = forms.CharField(widget=forms.PasswordInput(render_value=False),max_length=100)


TASKTYPES=[('', 'All'),]+ [(type.taskTypeDesignation,type.taskTypeDesignation) for type in TaskType.objects.all()]

TASK_RESULTS = (
    ('', 'All'),
    ('Ok', 'Ok'),
    ('Error', 'Error'),
    ('Not yet', 'Not yet'),
)

TASK_STATUS = (
    ('', 'All'),
    ('Sent to queue', 'Task in the queue'),
    ('In the worker', 'Task in the worker !'),
    ('Done', 'Task Done !'),
)

PROFILES = [(p.profDesignation,p.profDesignation) for p in Profile.objects.all()]


class SearchForm(forms.Form):
    #type_tache=forms.CharField(label='Type de l\'action',required=False)
    task_type=forms.ChoiceField(choices=TASKTYPES,label="Type of the action",required=False)
    task_result=forms.ChoiceField(choices=TASK_RESULTS,label="Result",required=False)
    task_status=forms.ChoiceField(choices=TASK_STATUS,label="Status",required=False)
    task_start_date=forms.DateTimeField(label="Date when the task has started",required=False)
    task_end_date=forms.DateTimeField(label="Date when the task has been finished",required=False)
    concerned_user=forms.CharField(label="Concerned User",required=False)


class QuickSearch(forms.Form):
    concerned_user=forms.CharField(label="Concerned User",required=False)

class EditProfile(forms.Form):
    
    user_profile = forms.ChoiceField(choices=PROFILES,label="User's profile",required=True)



class Tools(forms.Form):
    file  = forms.FileField()    



