from django.conf import settings
from django.utils.translation import ugettext as _
import os


DEBUG = getattr(settings, 'DEBUG')
BASE_DIR = getattr(settings, 'DEBUG')
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
ADMINS = getattr(settings, 'ADMINS', [])

APP = 'OHM2_HANDLERS_'

SAVE_RUN_EXCEPTIONS = getattr(settings, APP + 'SAVE_RUN_EXCEPTIONS', True)
SAVE_INPUT_EXCEPTIONS = getattr(settings, APP + 'SAVE_INPUT_EXCEPTIONS', True)
SAVE_METHOD_EXCEPTIONS = getattr(settings, APP + 'SAVE_METHOD_EXCEPTIONS', True)

PRINT_EXCEPTIONS = getattr(settings, APP + 'PRINT_EXCEPTIONS', True)

SAVE_STATISTICS = getattr(settings, APP + 'SAVE_STATISTICS', True)
SAVE_STATISTICS_EVERY_THIS_REQUESTS = getattr(settings, APP + 'SAVE_STATISTICS_EVERY_THIS_REQUESTS', 100)
STATATISTICS = {
	"total_requests" : 1,
	"average_request_time" : 0,
}


DETECT_DEVICE = getattr(settings, APP + 'DETECT_DEVICE', False)
DEVICE_IOS_NAME = getattr(settings, APP + 'IOS_NAME', "iOS")
DEVICE_ANDROID_NAME = getattr(settings, APP + 'ANDROID_NAME', "Android")
DEVICE_PC_NAME = getattr(settings, APP + 'PC_NAME', "Default")
SUPPORTED_DEVICES = (
	DEVICE_IOS_NAME.strip().lower(),
	DEVICE_ANDROID_NAME.strip().lower(),
	DEVICE_PC_NAME.strip().lower(),
)


DETECT_COUNTRY = getattr(settings, APP + 'DETECT_COUNTRY', False)
GEOIP_PATH = getattr(settings, APP + "GEOIP_PATH", os.path.join( os.path.dirname(os.path.realpath(__file__))) )
DETECT_LATITUDE_AND_LONGITUDE =  getattr(settings, APP + 'DETECT_LATITUDE_AND_LONGITUDE', False)


SAVE_SENT_EMAILS = getattr(settings, APP + 'SAVE_SENT_EMAILS', True)
MAILGUN_DOMAIN = getattr(settings, APP + 'MAILGUN_DOMAIN', "")
MAILGUN_API_KEY = getattr(settings, APP + 'MAILGUN_API_KEY', "")


CREATE_QR_CODES = getattr(settings, APP + 'CREATE_QR_CODES', False)
CREATE_BARCODES = getattr(settings, APP + 'CREATE_BARCODES', False)

ENCRYPTION_ENABLED = getattr(settings, APP + 'ENCRYPTION_ENABLED', True)
PILL_ENABLED = getattr(settings, APP + 'PILL_ENABLED', True)

BLOCKED_IPS = getattr(settings, APP + 'BLOCKED_IPS', [])

GOOGLE_RECAPTCHA_SECRET = getattr(settings, APP + 'GOOGLE_RECAPTCHA_SECRET', "")
GOOGLE_RECAPTCHA_VERIFY_URL = getattr(settings, APP + 'GOOGLE_RECAPTCHA_VERIFY_URL', "https://www.google.com/recaptcha/api/siteverify")

NOTIFY_LANDING_MESSAGE = getattr(settings, APP + 'NOTIFY_LANDING_MESSAGE', True)
NOTIFY_LANDING_EMAIL = getattr(settings, APP + 'NOTIFY_LANDING_EMAIL', True)







