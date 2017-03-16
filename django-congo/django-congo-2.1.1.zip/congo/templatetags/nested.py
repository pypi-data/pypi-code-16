# -*- coding: utf-8 -*-
from congo.templatetags import common
from django.template import Library

register = Library()

@register.simple_tag
def google_maps(mode, **kwargs):
    return common.google_maps(mode, **kwargs)
