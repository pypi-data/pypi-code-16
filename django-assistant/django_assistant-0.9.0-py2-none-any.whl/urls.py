from django.conf.urls import url

from . import views

urlpatterns = [
    
    url(r'^a_trial_api2/$', views.a_trial_api),
    
    url(r'^$', views.index, name='index'),
    url(r'^a_create_api/$', views.a_create_api),
    url(r'^a_get_apis/$', views.a_get_apis),
    url(r'^a_fetch_api_details/$', views.a_fetch_api_details),
    url(r'^a_edit_params/$', views.a_edit_params),
    url(r'^a_delete_api/$', views.a_delete_api),
    url(r'^a_edit_api_status/$', views.a_edit_api_status),
    
]


