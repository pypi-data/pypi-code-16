from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index_view, name='Index'),
    url(r'^login$', views.login_view, name='Login'),
    url(r'^logout$', views.logout_view, name='Logout'),
]
