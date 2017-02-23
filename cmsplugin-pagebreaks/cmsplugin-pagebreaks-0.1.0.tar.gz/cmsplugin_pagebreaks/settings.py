# coding: utf-8
from django.conf import settings

PAGE_GET_PARAMETER = getattr(settings, 'CMSPLUGIN_PAGEBREAKS_PAGE_GET_PARAMETER', 'page')
