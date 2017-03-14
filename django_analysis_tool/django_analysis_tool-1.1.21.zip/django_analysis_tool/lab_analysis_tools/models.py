#coding:utf-8
import os
from django.contrib import admin
# Create your models here.
from django.db import models

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')


class Task(models.Model):
    task_id = models.CharField(max_length=10)

    def __unicode__(self):
        return self.task_id

class Problem(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

class TaskDevice(models.Model):
    name = models.CharField(max_length=40)
    problems = models.ManyToManyField(Problem)
    task = models.ForeignKey(Task)
    result = models.CharField(max_length=10)
    fail_detail = models.CharField(max_length=200)
    luaunit_fail = models.TextField(default='')
    luaunit_pass = models.TextField(default='')
    solution = models.TextField(default='')

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('fail_detail',)

class TaskUnzip(models.Model):
    task = models.ForeignKey(Task)

    zipfile_num = models.CharField(max_length=10, default=0)
    zipfile_comment = models.CharField(max_length = 50)
    zipfile_device = models.TextField()

    valid_zipfile_num = models.CharField(max_length = 10, default=0)
    valid_zipfile_comment = models.CharField(max_length = 50)
    valid_zipfile_device = models.TextField()

    resultzip_num = models.CharField(max_length = 10, default=0)
    resultzip_comment = models.CharField(max_length = 50)
    resultzip_device = models.TextField()

    valid_resultzip_num = models.CharField(max_length = 10, default=0)
    valid_resultzip_comment = models.CharField(max_length = 50)
    valid_resultzip_device = models.TextField()

    def __unicode__(self):
        return self.task


class SuConnectedTimedOut(models.Model):
    task = models.ForeignKey(Task)
    tid = models.CharField(max_length=10)
    all_devices = models.TextField()
    timedout_devices = models.TextField()
    rate = models.FloatField()
    repeat_devices = models.TextField(default='')
    unstable_devices = models.TextField(default='')
    newbird_devices = models.TextField(default='')

    def __unicode__(self):
        return self.rate

class NotFoundResultZip(models.Model):
    task = models.ForeignKey(Task)
    tid = models.CharField(max_length=10)
    all_devices = models.TextField()
    problem_devices = models.TextField()
    repeat_devices = models.TextField(default='')
    unstable_devices = models.TextField(default='')
    newbird_devices = models.TextField(default='')

    def __unicode__(self):
        return self.rate



