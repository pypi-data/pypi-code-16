from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import views
from . import apis

app_name = "countries"

API_PREFIX = r'^countries/api/v(?P<version>[^/]+)'

urlpatterns = [
	url(r'countries/$', views.index, name = 'index'),		
]


urlpatterns += [
	url(API_PREFIX + r'/flag/code/$', apis.flag_code, name = 'api_flag_code'),
	url(API_PREFIX + r'/get-country$', apis.get_country, name = 'api_get_country'),
	url(API_PREFIX + r'/get-regions$', apis.get_regions, name = 'api_get_regions'),
	url(API_PREFIX + r'/get-provinces$', apis.get_provinces, name = 'api_get_provinces'),
	url(API_PREFIX + r'/get-communes$', apis.get_communes, name = 'api_get_communes'),
]


urlpatterns += [
	url(API_PREFIX + r'/get-user-addresses$', apis.get_user_addresses, name = 'api_get_user_addresses'),
	url(API_PREFIX + r'/create-user-address$', apis.create_user_address, name = 'api_create_user_address'),
]


