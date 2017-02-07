from django.conf.urls import url

from .views import csv_view_export

urlpatterns = [
    url(r'^view-export/(?P<view>.+)/$', csv_view_export),
]
