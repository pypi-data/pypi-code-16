from django.conf import settings
from django.utils.translation import ugettext as _
import os, pytz


DEBUG = getattr(settings, 'DEBUG')
BASE_DIR = getattr(settings, 'BASE_DIR')
STRING_SINGLE = getattr(settings, 'STRING_SINGLE')
STRING_SHORT = getattr(settings, 'STRING_SHORT')
STRING_MEDIUM = getattr(settings, 'STRING_MEDIUM')
STRING_NORMAL = getattr(settings, 'STRING_NORMAL')
STRING_LONG = getattr(settings, 'STRING_LONG')
STRING_DOUBLE = getattr(settings, 'STRING_DOUBLE')
HOST = getattr(settings, 'HOST')
SUBDOMAINS = getattr(settings, 'SUBDOMAINS')
PROTOCOL = getattr(settings, 'PROTOCOL')
HOSTNAME = getattr(settings, 'HOSTNAME')
WEBSITE_URL = getattr(settings, 'WEBSITE_URL')
STATIC_URL = getattr(settings, 'STATIC_URL')
STATIC_ROOT = getattr(settings, 'STATIC_ROOT')
MEDIA_URL = getattr(settings, 'MEDIA_URL')
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')

APP = 'OHM2_HANDLERS_ACCOUNTS_'

SAVE_RUN_EXCEPTIONS = getattr(settings, APP + 'SAVE_RUN_EXCEPTIONS', True)
SAVE_INPUT_EXCEPTIONS = getattr(settings, APP + 'SAVE_INPUT_EXCEPTIONS', True)
SAVE_METHOD_EXCEPTIONS = getattr(settings, APP + 'SAVE_METHOD_EXCEPTIONS', True)

DEFAULT_COUNTRY = getattr(settings, APP + 'DEFAULT_COUNTRY')
DEFAULT_CURRENCY = getattr(settings, APP + 'DEFAULT_CURRENCY')
DEFAULT_TZ = getattr(settings, APP + 'DEFAULT_TZ')
AVATARS_UPLOAD_TO = getattr(settings, APP + 'AVATARS_UPLOAD_TO', "accounts/avatars/")
AVATARS_WEBSITE_URL = getattr(settings, APP + 'AVATARS_WEBSITE_URL', WEBSITE_URL)
CHECK_PASSWORD_SECURE = getattr(settings, APP + 'CHECK_PASSWORD_SECURE', True) # check is the user's password is secured based on AUTH_PASSWORD_VALIDATORS
SIGNUPS_ENABLED = getattr(settings, APP + 'SIGNUPS_ENABLED', True) # If False, signups will always fail
ENABLE_EMAIL_LOGIN = getattr(settings, APP + 'ENABLE_EMAIL_LOGIN', True) # set to True if users can login with their email too (username first then email)
UNIQUE_USER_EMAILS = getattr(settings, APP + 'UNIQUE_USER_EMAILS', False) # if set, the backend must garantee unique emails

PASSWORD_RESET_TEMPLATE_PATH = getattr(settings, APP + 'PASSWORD_RESET_TEMPLATE_PATH', os.path.join( os.path.dirname(os.path.realpath(__file__)), "templates/accounts/password_reset.html" ))
PASSWORD_RESET_FROM_EMAIL = getattr(settings, APP + 'PASSWORD_RESET_FROM_EMAIL', "no-reply@" + HOST)
PASSWORD_RESET_SUBJECT = getattr(settings, APP + 'PASSWORD_RESET_SUBJECT', "Password reset")
PASSWORD_RESET_SEND_ENABLE = getattr(settings, APP + 'PASSWORD_RESET_SEND_ENABLE', True) ## is False, email will not be send to the user
TIMEZONES = pytz.common_timezones
AUTH_PASSWORD_VALIDATORS = settings.AUTH_PASSWORD_VALIDATORS
REFERAL_CODE_LENGTH = getattr(settings, APP + 'REFERAL_CODE_LENGTH', 5)
LANGUAGE_CODE = getattr(settings, 'LANGUAGE_CODE')
LANGUAGES = getattr(settings, 'LANGUAGES')
MAX_USERNAME_LENGTH = getattr(settings, 'HANDLERS_MAX_USERNAME_LENGTH', 30)
MAX_FIRST_NAME_LENGTH = getattr(settings, 'HANDLERS_MAX_FIRST_NAME_LENGTH', 30)
MAX_LAST_NAME_LENGTH = getattr(settings, 'HANDLERS_MAX_LAST_NAME_LENGTH', 30)


PRESIGNUPS_ENABLED = getattr(settings, APP + 'PRESIGNUPS_ENABLED', False) # if True, an email will be sent with a link to continue with the signup process
PRESIGNUP_TEMPLATE_PATH =getattr(settings, APP + 'PRESIGNUP_TEMPLATE_PATH', os.path.join( os.path.dirname(os.path.realpath(__file__)), "templates/accounts/presignup.html" ))
PRESIGNUP_FROM_EMAIL = getattr(settings, APP + 'PRESIGNUP_FROM_EMAIL', "no-reply@" + HOST)
PRESIGNUP_SUBJECT = getattr(settings, APP + 'PRESIGNUP_SUBJECT', _("Signup step one"))
SIGNUP_USERNAME_TRUNCATION = getattr(settings, APP + 'SIGNUP_USERNAME_TRUNCATION', False)
LOGIN_USERNAME_TRUNCATION = getattr(settings, APP + 'LOGIN_USERNAME_TRUNCATION', False)
MINIMUM_PASSWORD_RESET_DELAY = getattr(settings, APP + 'MINIMUM_PASSWORD_RESET_DELAY', 30)

ENABLE_ALIAS_LOGIN = getattr(settings, APP + 'ENABLE_ALIAS_LOGIN', False)

SIGNUP_PIPELINE = getattr(settings, APP + 'SIGNUP_PIPELINE', (
	'ohm2_handlers.accounts.pipelines.signup.user_settings',
	'ohm2_handlers.accounts.pipelines.signup.user_keys',
	'ohm2_handlers.accounts.pipelines.signup.user_avatars',
	'ohm2_handlers.accounts.pipelines.signup.user_referalcode',
	'ohm2_handlers.accounts.pipelines.signup.user_authtoken',
	'ohm2_handlers.accounts.pipelines.signup.user_crypto',
))

LOGOUT_PIPELINE = getattr(settings, APP + 'LOGOUT_PIPELINE', (
	'ohm2_handlers.accounts.pipelines.logout.default',
))

LOGIN_PIPELINE = getattr(settings, APP + 'LOGIN_PIPELINE', (
	'ohm2_handlers.accounts.pipelines.login.default',
))


