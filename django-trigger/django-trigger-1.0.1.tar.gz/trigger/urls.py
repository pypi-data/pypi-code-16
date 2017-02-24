from django.conf.urls import include, url
import views

urlpatterns = [
	url(r'^verify/(?P<session_id>\w+)/$', views.verify),
	url(r'^email/(?P<reporte>\w+)/$', views.test_email),
	url(r'^calendar/$', views.calendar),
	url(r'^schedule/$', views.schedule),
	url(r'^error/', views.error),
	url(r'^connections/', views.connections),
]

