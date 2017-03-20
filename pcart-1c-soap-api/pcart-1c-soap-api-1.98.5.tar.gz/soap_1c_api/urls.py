from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from soap_1c_api.webservice import ExchangeWebService
from soap_server.soap import Application

application_view = Application(
    [ExchangeWebService], 'ws', name='ws').as_django_view()

urlpatterns = [
    url(r'^exchange/$', csrf_exempt(application_view))
]
