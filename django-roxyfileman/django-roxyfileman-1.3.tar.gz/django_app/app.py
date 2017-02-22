import os
from django_micro import configure, route, run

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
DEBUG = True

ROXY_ROOT = os.path.join(MEDIA_ROOT, 'uploads')
ROXY_VIEW_DECORATOR = 'django_app.auth.auth_decorator'


INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'roxyfileman',
]

configure(locals())

from django.conf.urls import include

route(r'^roxyfileman/', include('roxyfileman.urls'))

application = run()
