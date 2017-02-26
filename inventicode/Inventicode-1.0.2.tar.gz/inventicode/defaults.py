# -*- coding: utf-8 -*-
WEBSOCKET_URL = None
USE_CELERY = False
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'unique-snowflake'}}
BARCODE_PREFIX = 123000000000
DF_SYSTEM_CHECKS = []
LOGIN_URL = '/admin/login/'


DF_INDEX_VIEW = 'inventicode.views.index'
DF_SITE_SEARCH_VIEW = None
DF_PROJECT_NAME = 'InventiCode'
DF_URL_CONF = '{DF_MODULE_NAME}.urls.urlpatterns'
DF_REMOTE_USER_HEADER = None  # HTTP-REMOTE-USER
