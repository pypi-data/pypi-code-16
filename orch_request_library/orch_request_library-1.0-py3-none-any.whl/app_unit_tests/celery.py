from CeleryConfig import *


app = CeleryConfig.create("logs")
app2 = CeleryConfig.create("server")
app3 = CeleryConfig.create("av")


from django.conf.celery import app_unit_tests


app.sendTask("jobs.update",newval)