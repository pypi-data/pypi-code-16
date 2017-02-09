from django.conf.urls import url

from . import views

app_name = 'simpleauth'
urlpatterns = [
    url(r'^$', views.start, name='start'),
    url(r'register/$', views.register, name='register'),
]
