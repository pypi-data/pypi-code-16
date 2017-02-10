from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.login_view, name='Login'),
    url(r'^login$', views.login_view),
]
