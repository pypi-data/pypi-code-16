from django.conf.urls import url
from django.views.generic.base import RedirectView
from axes.decorators import watch_login
from . import views
from . import apis

app_name = "accounts"

API_PREFIX = r'^accounts/api/v(?P<version>[^/]+)'

urlpatterns = [
	url(r'^accounts/logout$', views.logout, name = 'logout'),
	url(r'^accounts/check-user-integrity-and-redirect/$', views.check_user_integrity_and_redirect, name = 'check_user_integrity_and_redirect'),
]

urlpatterns += [
	url(API_PREFIX + r'/signup$', apis.signup, name = 'api_signup'),
	url(API_PREFIX + r'/login$', watch_login(apis.login), name = 'api_login'),
	url(API_PREFIX + r'/logout$', apis.logout, name = 'api_logout'),
]


urlpatterns += [
	url(API_PREFIX + r'/change-password$', apis.change_password, name = 'api_change_password'),
	url(API_PREFIX + r'/reset-password-step-one$', apis.reset_password_step_1, name = 'api_reset_password_step_1'),
	url(API_PREFIX + r'/reset-password-step-two$', apis.reset_password_step_2, name = 'api_reset_password_step_2'),
]


urlpatterns += [
	url(API_PREFIX + r'/signup-and-login$', apis.signup_and_login, name = 'api_signup_and_login'),
]

urlpatterns += [
	url(API_PREFIX + r'/update-avatars$', apis.update_avatars, name = 'api_update_avatars'),
	url(API_PREFIX + r'/update-settings$', apis.update_settings, name = 'api_update_settings'),
	url(API_PREFIX + r'/update-user-password$', apis.update_user_password, name = 'api_update_user_password'),
	url(API_PREFIX + r'/update-user-information$', apis.update_user_information, name = 'api_update_user_information'),
]


urlpatterns += [
	url(API_PREFIX + r'/facebook-signup$', apis.facebook_signup, name = 'api_facebook_signup'),
]


urlpatterns += [
	url(API_PREFIX + r'/presignup-step-one$', apis.presignup_step_one, name = 'api_presignup_step_one'),
	url(API_PREFIX + r'/presignup-step-two$', apis.presignup_step_two, name = 'api_presignup_step_two'),
]


urlpatterns += [
	url(API_PREFIX + r'/update-alias$', apis.update_alias, name = 'api_update_alias'),
]