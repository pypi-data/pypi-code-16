# Django settings for smitSite project.
import os
import sys, datetime
import shutil
from distutils import dir_util
from configobj import ConfigObj
ROOT_PATH    = os.path.dirname(__file__)

#set config that will be used by applications
SMIT_CONFIG = ConfigObj("smit.ini")
if SMIT_CONFIG =={}:
    print "ATTENTION: smit.ini file is not valid"


#applications folder contains all new applications
APPLICATIONS = os.path.join(ROOT_PATH, "applications")
sys.path.insert(0, APPLICATIONS)
#this variable contains a list of directories in applications folder
NEW_APPLICATIONS = tuple([folderName for folderName in os.listdir(APPLICATIONS) if folderName != ".svn"])
#this variable contains tuple of the new applications template targets
NEW_APPLICATIONS_TEMPLATES = tuple([os.path.join(ROOT_PATH, folderName, 'templates') for folderName in NEW_APPLICATIONS])

#add workers to media/workers/ ==> this is important in order to make tasks downoadable by workers
MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')
MEDIA_URL = ''
workers_dir = os.path.join(MEDIA_ROOT, "workers")
linux_tasks_list = []
windows_tasks_list = []
#callback for walk to copy worker tasks for each application to the folder shown via the web ...(for an eventual download by workers)
def processDirectory (args, dirname, filenames):
    if (("LinuxWorker" in dirname) or ("WindowsWorker" in dirname)) and (".svn" not in dirname):
        for filename in filenames:
            if ".svn" not in filename:
                shutil.copy(os.path.join(dirname, filename), os.path.join(workers_dir, dirname.split('/')[-1], filename))
                if ("LinuxWorker" in dirname):
                    linux_tasks_list.append(filename)
                else:
                    windows_tasks_list.append(filename)

for application in NEW_APPLICATIONS:
    app_target = os.path.join(ROOT_PATH, "applications", application)
    os.path.walk(app_target, processDirectory, None)

tasks_list_file_windows = open (os.path.join(workers_dir, "WindowsWorker", "tasks_list.py"), 'wb+')
tasks_list_file_linux = open (os.path.join(workers_dir, "LinuxWorker", "tasks_list.py"), 'wb+')
tasks_list_file_linux.write("tasks_list="+str(linux_tasks_list))
tasks_list_file_linux.close()
tasks_list_file_windows.write("tasks_list="+str(windows_tasks_list))
tasks_list_file_windows.close()

DEBUG = True
TEMPLATE_DEBUG = DEBUG


ADMINS = (
    ('admin', 'admin@starxpert.fr'),

)
SESSION_COOKIE_AGE = 7200
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_VHOST = "/"
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
CELERY_RESULT_BACKEND = 'amqp'
#BROKER_BACKEND = "RabbitMQ"
CELERYD_CONCURRENCY = 2
#CELERY_IMPORTS = ("imap.tasks","pst.tasks",)
#CACHE_BACKEND = 'memcached://10.1.0.134:11211/'
CELERYD_LOG_FILE = "/var/log/smit/server.log"
#CELERYD_LOG_LEVEL = "INFO"

#MANAGERS = ADMINS
#DATABASE_ENGINE = 'mysql'          # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#DATABASE_NAME = "smit"             # Or path to database file if using sqlite3.
#DATABASE_USER = 'root'             # Not used with sqlite3.
#DATABASE_PASSWORD = 'null!null'         # Not used with sqlite3.
#DATABASE_HOST = 'localhost'        # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = '3306'             # Set to empty string for default. Not used with sqlite3.
DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'smit', # Or path to database file if using sqlite3.
        'USER': 'root', # Not used with sqlite3.
        'PASSWORD': 'UALrdb62', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}


#################adds#################"

CELERY_DEFAULT_QUEUE = "server_tasks"
CELERY_QUEUES = {
        "server_tasks": {
        "binding_key": "server.#",
        },
        }
CELERY_DEFAULT_EXCHANGE = "tasks"
CELERY_DEFAULT_EXCHANGE_TYPE = "topic"
CELERY_DEFAULT_ROUTING_KEY = "task.server"
#CELERYD_LOG_FILE = "/var/log/celery/%s.log"%str(datetime.datetime.now())


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-FR'
DEFAULT_CHARSET = 'utf-8'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

#MEDIA_ROOT = "/home/khalil/workspace/testDjango/src/css"




STATIC_URL = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'x(@h=!m&2pjux!x30h#&rls0*q*lphzgz(=pn&)wt@vna68o)%'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader'
)





MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #"/home/khalil/workspace/NewZimbraSmit/src/smitSite/templates"
    os.path.join(ROOT_PATH, 'main', 'templates'),

)+NEW_APPLICATIONS_TEMPLATES

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'djcelery',
    'main',
    'mini_url',
    'bootstrap3',
    'bootstrapform', 
    'django_forms_bootstrap',	
)+NEW_APPLICATIONS

#inrets
import djcelery
djcelery.setup_loader()

# Name of the projects settings module.
#export DJANGO_SETTINGS_MODULE="settings"
