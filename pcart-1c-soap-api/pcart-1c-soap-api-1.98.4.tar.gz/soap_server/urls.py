#-*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from soap_server.webservice import DemoWebService
from soap_server.soap import Application
from django.conf import settings
'''
Since the list of applications will end up in the same namespace, make sure you 
don't have two types or methods called the same!

Notice how we must wrap the resulting view in a csrf_exempt() call? 
This is absolutely necessary since it would otherwise diverge from the RFC and 
thus would require custom webservice clients. 
'''

SOAP_SERVER_DEMO = getattr(settings, 'SOAP_SERVER_DEMO', True)

# This is just for readability's sake
application_view = Application([DemoWebService], 'ws', name='ws').as_django_view()

urlpatterns = patterns('')

if SOAP_SERVER_DEMO:
    urlpatterns += patterns('',
        url(r'^demo/', csrf_exempt(application_view))
    )
