# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import signals


class Department(models.Model):
    """ @DynamicAttrs """
    depId = models.AutoField(primary_key=True)
    depDesignation = models.CharField(max_length = 384)

    def __unicode__(self):
        return self.depDesignation
    class Meta:
        db_table = u'Department'

class Profile(models.Model):
    """ @DynamicAttrs """
    profId= models.AutoField(primary_key=True)
    profDesignation = models.CharField(max_length = 384)
    def __unicode__(self):
        return self.profDesignation
    class Meta:
        db_table = u'Profile'

class Usr(models.Model):
    """ @DynamicAttrs """
    userId = models.AutoField(primary_key=True)
    userEmail=models.EmailField(unique=True)
    userName = models.CharField(max_length=50)
    #it might be better to don't have the user password here ?
    #userPassword = models.CharField(max_length=765)
    department = models.ForeignKey(Department)
    profile = models.ForeignKey(Profile)
    isAdmin=models.BooleanField(default=False)
    #parent = models.ForeignKey('self', null=True,blank=True)
    class Meta:
        db_table = u'Usr'


    def __unicode__(self):
        return self.userEmail

class Auth_csv(models.Model):
    """ @DynamicAttrs """
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=765)
    class Meta:
        db_table = u'Auth_csv'


class UserManager(models.Model):
    """ @DynamicAttrs """
    usr = models.OneToOneField(Usr)
#    mngrPassword = models.CharField(max_length=384)
    managedDepartments = models.ManyToManyField(Department)

    def __unicode__(self):
        return self.usr.userEmail

    class Meta:
        db_table = u'UserManager'

#this function update isAdmin in Usr class in order to simplify checking user if he is an Admin or not !
def setAdmin(sender, instance, **kwargs):
    user = instance.usr
#    if user.isAdmin == False:
#        user.isAdmin = True
#    else:
    user.isAdmin = True
    user.save(force_update=True)
signals.post_save.connect(setAdmin, sender=UserManager)



class TaskType(models.Model):
    taskTypeId = models.AutoField(primary_key=True)
    managers = models.ManyToManyField(UserManager,related_name='managers')
    taskTypeDesignation = models.CharField(unique=False,max_length=384)
    taskTypeDescription = models.CharField(null=True,max_length=384)
    #I'd like not to add this here, but I didn't have other choices...
    profile = models.ManyToManyField(Profile)
    def __unicode__(self):
        return self.taskTypeDesignation
    class Meta:
        db_table = u'TaskType'


RESULT_CHOICES=(('0','Error',),('1','Ok'),('2','Not yet'))
STATUS_CHOICES=(('0','Sent to queue'),('1','In the worker',),('2','Done'))


class SmitTask(models.Model):
    taskId = models.CharField(max_length=254, primary_key=True, unique=False)
    usr = models.ForeignKey(Usr)
    taskType = models.ForeignKey(TaskType)
    smitName = models.CharField(null=True,max_length=200)
    smitConcernedEmail = models.EmailField(null=True)
    smitStatus = models.CharField(null=True,max_length=50)#choices= STATUS_CHOICES,max_length=1)
    smitWorkerName = models.CharField(null=True,max_length=384)
    smitResult = models.CharField(null=True,max_length=50)
    smitStartDate = models.DateTimeField(null=True)
    smitInWorkerDate = models.DateTimeField(null=True)
    smitEndDate = models.DateTimeField(null=True)
    smitLogFile = models.CharField(null=True,max_length=384,blank=True)

    def __unicode__(self):
        return self.taskId
    class Meta:
        db_table = u'SmitTask'

class CeleryTaskmeta(models.Model):
    id = models.IntegerField(primary_key=True)
    task_id = models.CharField(unique=False, max_length=765)
    status = models.CharField(max_length=150)
    result = models.TextField(blank=True,null=True)
    date_done = models.DateTimeField()
    traceback = models.TextField(blank=True,null=True)
    class Meta:
        db_table = u'celery_taskmeta'

class CeleryTasksetmeta(models.Model):
    id = models.IntegerField(primary_key=True)
    taskset_id = models.CharField(unique=False, max_length=765)
    result = models.TextField(blank=True,null=True)
    date_done = models.DateTimeField()
    class Meta:
        db_table = u'celery_tasksetmeta'







