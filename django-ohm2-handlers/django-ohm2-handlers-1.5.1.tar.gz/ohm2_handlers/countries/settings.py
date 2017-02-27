from django.conf import settings
from django.utils.translation import ugettext as _
import os


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

APP = 'OHM2_HANDLERS_COUNTRIES_'

SAVE_RUN_EXCEPTIONS = getattr(settings, APP + 'SAVE_RUN_EXCEPTIONS', True)
SAVE_INPUT_EXCEPTIONS = getattr(settings, APP + 'SAVE_INPUT_EXCEPTIONS', True)
SAVE_METHOD_EXCEPTIONS = getattr(settings, APP + 'SAVE_METHOD_EXCEPTIONS', True)

FLAGS_PATH = getattr(settings, APP + 'FLAGS_PATH', os.path.join( os.path.dirname(os.path.realpath(__file__)), "static", "countries", "default", "images", "flags"))
FLAG_URL = getattr(settings, APP + 'FLAG_URL', "/countries/flags")
FLAG_SIZES = ["16", "24", "32", "48"]