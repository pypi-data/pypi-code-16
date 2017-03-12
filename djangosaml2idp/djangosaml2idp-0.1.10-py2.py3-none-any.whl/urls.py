from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', views.login_begin, name="saml_login_begin"),
    url(r'^login/process/$', views.login_process, name='saml_login_process'),
    url(r'^metadata/$', views.metadata, name='saml2_idp_metadata'),
]
