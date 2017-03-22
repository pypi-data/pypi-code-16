from django.db import models
import uuid
from django.utils import timezone

# Create your models here.

class VisaDevice(models.Model):
    active = models.BooleanField(default=True)
    connected = models.BooleanField(default=False)
    alias = models.CharField(max_length=200, default=str(uuid.uuid4()))
    address = models.CharField(max_length=200)

    def log(self):
        return self.visaevent_set.all()

    def query(self, request, response, success):
        r = self.visaevent_set.create(request=request, response=response, execution_date=timezone.now(), success=success, operation='query')
        r.save()
        return r

    def read(self, request, response, success):
        r = self.visaevent_set.create(request=request, response=response, execution_date=timezone.now(), success=success, operation='read')
        r.save()
        return r

    def write(self, request, response, success):
        r = self.visaevent_set.create(request=request, response=response, execution_date=timezone.now(), success=success, operation='write')
        r.save()
        return r

class VisaEvent(models.Model):
    session = models.ForeignKey(VisaDevice, on_delete=models.CASCADE)
    request = models.CharField(max_length=200, default="?IDN")
    response = models.CharField(max_length=200)
    execution_date = models.DateTimeField('date published')
    operation = models.CharField(max_length=200, default="query")
    success = models.BooleanField(default=False)

