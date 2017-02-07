import os
from shuup.utils.setup import Setup
from shuup.addons import add_enabled_addons
from shuup_workbench.settings.utils import DisableMigrations

from shuup_dev_testutils.settings_base import *


#------------------------------------------------------------------------------
# django
#------------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'attrim',
        'USER': 'attrim',
        'PASSWORD': 'attrim',
        'HOST': 'postgres',
        'PORT': 5432,
    }
}

#------------------------------------------------------------------------------
# directories
#------------------------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
MEDIA_ROOT = os.path.join(BASE_DIR, 'var', 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'var', 'static')

#------------------------------------------------------------------------------
# apps and middleware
#------------------------------------------------------------------------------

SHUUP_ENABLED_ADDONS_FILE = os.path.join(BASE_DIR, 'var', 'enabled_addons')

installed_attrim_apps = [
    'attrim',
]

INSTALLED_APPS = add_enabled_addons(
    addon_filename=SHUUP_ENABLED_ADDONS_FILE,
    apps=INSTALLED_APPS_SHUUP_DEFAULT + installed_attrim_apps,
)

#------------------------------------------------------------------------------
# test settings
#------------------------------------------------------------------------------

if os.environ.get('IS_SHUUP_TEST_LOCAL') == '1':
    DATABASES['default']['USER'] = 'django'
    DATABASES['default']['PASSWORD'] = '0KjyugEIqCg4uNGTyTy8'
    DATABASES['default']['HOST'] = 'localhost'
