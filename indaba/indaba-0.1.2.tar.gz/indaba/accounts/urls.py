from django.conf.urls import  include, url

from django.contrib import admin

from .views import SignUpView, LoginView, LogOutView

urlpatterns = [
    url(r'accounts/register/$', SignUpView.as_view(), name='signup'),
    url(r'accounts/login/$', LoginView.as_view(), name='login'),
    url(r'accounts/logout/$', LogOutView.as_view(), name='logout'),

]
