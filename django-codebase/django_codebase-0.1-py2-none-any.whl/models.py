from __future__ import unicode_literals

from django.db import models

# Create your models here.


HTTP_CHOICES = [("post","POST"),("get","GET")]

class Api(models.Model):
    url = models.CharField(max_length=200,unique=True)
    desc = models.CharField(max_length=200)
    params = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    http_type =  models.CharField(max_length=10,choices = HTTP_CHOICES)
    def __str__(self):
	return self.url
