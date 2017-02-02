from django.conf.urls import url
import views

urls = [
     url(r'^charts/(?P<chart_id>[\w ]+\.json)/$', views.dispatch_chart),
     url(r'^reports/(?P<chart_id>[\w ]+\.xls)/$', views.dispatch_xls),
     url(r'^show_reports.json/$', views.dispatch_group_reports_as_json),
     url(r'^show_reports/$', views.dispatch_group_reports),
     url(r'^show_groups/$', views.dispatch_groups),
     url(r'^get_chart_configs.json/$', views.dispatch_chart_configurations),
     url(r'^get_group_filters.json/$', views.dispatch_group_filters_as_json),
     url(r'^download_docx/$', views.download_as_docx),
      ]

