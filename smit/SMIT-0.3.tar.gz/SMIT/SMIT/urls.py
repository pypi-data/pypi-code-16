"""SMIT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""


from __future__ import absolute_import
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
import django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles import views
from main.views import showSmitStatistics
from main.views import index
from main.views import logout
from main.views import cancelTask
from main.views import search
from main.views import showCeleryStatistics
from main.views import upload_file
from main.views import deleteAll
from main.views import cancelListTasks
from main.views import showLog
from main.views import myResult
from main.views import getListUsers
from main.views import editUserProfile
from main.views import runApplications
from main.views import checkNetwork
from main.views import tools
from SMIT.settings import NEW_APPLICATIONS
##import url_writter

admin.autodiscover()

list_new_applications = NEW_APPLICATIONS


urlpatterns = [
    url(r'^admin/', admin.site.urls), 
    url(r'^media/(?P<path>.*)$',django.views.static.serve),
    url(r'^$', index),
    url(r'^index/', index),
    url(r'^logout/', logout),
    url(r'^up/', upload_file),
    url(r'^showCeleryStatistics/' , showCeleryStatistics),
    url(r'^showLog/', showLog),
    url(r'^delete_all/' , deleteAll),
    url(r'^cancelTask/$', cancelTask),
    url(r'^cancelListTasks/', cancelListTasks),
    url(r'^search/', search),
    url(r'^smitUser/showResults/', myResult),
    url(r'^applications/run', runApplications),
    url(r'^smitAdmin/checkNetwork', checkNetwork),
    url(r'^smitAdmin/tools', tools),
    url(r'^smitAdmin/listUsers/', getListUsers),
    url(r'^smitAdmin/editProfile/$', editUserProfile),
    url(r'^smitAdmin/showResults/' , showSmitStatistics),
] + static(settings.STATIC_URL, document_root=settings.MEDIA_ROOT)

for app in list_new_applications:
    urlpatterns += [
	   url(r'^%s/'% app, include('%s.urls'%app)),
    ]
