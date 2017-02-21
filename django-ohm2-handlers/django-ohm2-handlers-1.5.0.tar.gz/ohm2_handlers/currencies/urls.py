from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import views
from . import apis

app_name = "currencies"

API_PREFIX = r'^currencies/api/v(?P<version>[^/]+)'

urlpatterns = [
	url(r'currencies/$', views.index, name = 'index'),		
]


urlpatterns += [
	url(API_PREFIX + r'/$', apis.index, name = 'api_index'),		
]


