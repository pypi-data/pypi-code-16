from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import apis

app_name = "ohm2_handlers"

API_PREFIX = r'^ohm2-handlers/api/v(?P<version>[^/]+)'

urlpatterns = []

urlpatterns += [
	url(API_PREFIX + r'/create-landing-message$', apis.create_landing_message, name = 'api_' + 'create_landing_message'),
	url(API_PREFIX + r'/create-landing-email$', apis.create_landing_email, name = 'api_' + 'create_landing_email'),
]
