"""LabResult URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from . import views
from django.conf.urls import url, include

urlpatterns = [
    # ex: /lab_analysis_tools/index/
    url(r'^index/$', views.index, name='index'),
    # ex: /lab_analysis_tools/task_id/title=xxxx
    url(r'^(?P<task_id>.*)/title=(?P<title>.*)/$',views.title, name = 'title'),
    # ex: /lab_analysis_tools/all/xxxx
    url(r'^all/(?P<task_id>.*)$',views.all,name = 'all'),
    # ex: /lab_analysis_tools/allUnzip
    url(r'^allUnzip/$',views.allUnzip,name = 'allUnzip'),
    # ex: /lab_analysis_tools/his_all/xxxx
    url(r'^his_all/(?P<task_id>.*)$',views.his_all, name = 'his_all'),
    # ex: /lab_analysis_tools/run_analysis/xxxx
    # url(r'^run_analysis/(?P<task_id>.*)$', views.run_analysis, name="run_analysis"),
    # ex: /lab_analysis_tools/zip/
    url(r'^zip/$', views.zip, name='zip'),
     # ex: /lab_analysis_tools/zipProcess/
    url(r'^zipProcess/$',views.zipProcess, name='zipProcess'),
    # ex: /lab_analysis_tools/config/xxxx/
    # url(r'^config/(?P<task_id>.*)$', views.config, name='config'),
    # ex: /lab_analysis_tools/export/
    url(r'^export/$', views.export, name='export'),
    # ex: /lab_analysis_tools/export_zip/
    url(r'^export_zip/$', views.export_zip, name='export_zip'),
    # ex: /lab_analysis_tools/task_id/fail_detail=xxxx/
    url(r'^(?P<task_id>.*)/fail_detail=(?P<detail>.*)/$',views.fail_detail, name = 'fail_detail'),
    # ex: /lab_analysis_tools/zip_process=xxxx/
    url(r'^zip_process=(?P<parameter>.*)/$',views.zip_process, name='zip_process'),
    # ex: /lab_analysis_tools/delete_task/xxxx
    url(r'^delete_task/(?P<task_id>.*)$', views.delete_task, name='delete_task'),
    # ex: /lab_analysis_tools/trend_su/
    # url(r'^trend_su/$', views.trend_su, name='trend_su'),
    # ex: /lab_analysis_tools/su_proportionPercentage/
    # url(r'^su_proportionPercentage/$', views.su_proportionPercentage, name='su_proportionPercentage'),
    # ex: /lab_analysis_tools/su_stability/
    # url(r'^su_stability/$', views.su_stability, name='su_stability'),
    # ex: /lab_analysis_tools/su_searchbydevice/
    # url(r'^su_searchbydevice/$', views.su_searchbydevice, name='su_searchbydevice'),
    # ex: /lab_analysis_tools/notFoundResultZip/
    # url(r'^notFoundResultZip/$', views.notFoundResultZip, name='notFoundResultZip'),
    # ex: /lab_analysis_tools/luaunit/xxxx
    url(r'^luaunit/(?P<task_id>.*)$', views.luaunit, name="luaunit"),
    # ex: /lab_analysis_tools/luaunit/xxxx/
    url(r'^luaunit_devices/(?P<devices>.*)/$', views.luaunit_devices, name="luaunit_devices"),
    # ex: /lab_analysis_tools/export_luaunit/task_id
    url(r'^export_luaunit/(?P<task_id>.*)$', views.export_luaunit, name='export_luaunit'),

]