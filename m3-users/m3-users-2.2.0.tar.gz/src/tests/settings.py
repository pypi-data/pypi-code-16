# Django settings for m3project project.

#import logging

#from m3.helpers import logger

DEBUG = True
TEMPLATE_DEBUG = DEBUG

TEST_RUNNER = 'm3.contrib.tests.M3TestSuiteRunner'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

#DATABASE_ENGINE = 'postgresql_psycopg2'  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#DATABASE_NAME = 'tests'              # Or path to database file if using sqlite3.
#DATABASE_USER = 'tests'               # Not used with sqlite3.
#DATABASE_PASSWORD = 'tests'             # Not used with sqlite3.
#DATABASE_HOST = 'localhost'              # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = ''                   # Set to empty string for default. Not used with sqlite3.

#DATABASE_ENGINE = 'sqlite3'  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#DATABASE_NAME = 'tests'              # Or path to database file if using sqlite3.
#DATABASE_USER = 'tests'               # Not used with sqlite3.
#DATABASE_PASSWORD = 'tests'             # Not used with sqlite3.
#DATABASE_HOST = 'localhost'              # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = ''                   # Set to empty string for default. Not used with sqlite3.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'tests',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-RU'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'm)g5cxsgr)#wc=j9ld7%7j5-bg+xz54*cvnl8cjm7tbl=1z)y='

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'm3.core.middleware.M3CommonMiddleware',
)

ROOT_URLCONF = 'tests.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.auth',
    'south',
    'm3_smthng',
    'tests.core',
)

#logger.init_logging('./logs')
