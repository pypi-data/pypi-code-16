# -*- coding: utf-8 -*-
from django.utils.translation import to_locale, get_language
from django.utils.translation.trans_real import parse_accept_lang_header
from moneyed.localization import _FORMATTER as FORMATTER, DEFAULT as DEFAULT_FORMAT
import re

language_code_re = re.compile(
    r'^[a-z]{1,8}(?:-[a-z0-9]{1,8})*(?:@[a-z0-9]{1,20})?$',
    re.IGNORECASE
)

def get_money_locale(locale = None):
    if locale is None:
        locale = to_locale(get_language())

    locale_list = FORMATTER.formatting_definitions.keys()
    if locale not in locale_list:
        for l in locale_list:
            if l.split('_')[0].upper() == locale.split('_')[0].upper():
                return l

    return DEFAULT_FORMAT.upper()

def get_accept_language_from_request(request, default = ''):
    accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    for accept_lang, unused in parse_accept_lang_header(accept):
        if accept_lang == '*':
            break

        if not language_code_re.search(accept_lang):
            continue

        return accept_lang.split('-')[0]

    return default
