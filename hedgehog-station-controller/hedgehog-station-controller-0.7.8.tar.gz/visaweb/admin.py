from django.contrib import admin

# Register your models here.
from .models import VisaDevice, VisaEvent

admin.site.register(VisaDevice)
admin.site.register(VisaEvent)