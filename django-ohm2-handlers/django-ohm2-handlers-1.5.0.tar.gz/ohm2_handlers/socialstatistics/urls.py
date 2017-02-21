from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import views
from . import apis

app_name = "socialstatistics"

API_PREFIX = r'^socialstatistics/api/v(?P<version>[^/]+)'

urlpatterns = [
	url(r'socialstatistics/$', views.index, name = 'index'),		
]


urlpatterns += [
	url(API_PREFIX + r'/twitter-authorization-url$', apis.twitter_authorization_url, name = 'api_twitter_authorization_url'),
	url(API_PREFIX + r'/twitter-get-access-token$', apis.twitter_get_access_token, name = 'api_twitter_get_access_token'),
	url(API_PREFIX + r'/twitter-delete-account$', apis.twitter_delete_account, name = 'api_twitter_delete_account'),
]


urlpatterns += [
	url(API_PREFIX + r'/facebook-authorization-url$', apis.facebook_authorization_url, name = 'api_facebook_authorization_url'),
	url(API_PREFIX + r'/facebook-get-access-token$', apis.facebook_get_access_token, name = 'api_facebook_get_access_token'),
	url(API_PREFIX + r'/facebook-delete-account$', apis.facebook_delete_account, name = 'api_facebook_delete_account'),
	url(API_PREFIX + r'/facebook-delete-page$', apis.facebook_delete_page, name = 'api_facebook_delete_page'),
	url(API_PREFIX + r'/facebook-create-page$', apis.facebook_create_page, name = 'api_facebook_create_page'),
]
