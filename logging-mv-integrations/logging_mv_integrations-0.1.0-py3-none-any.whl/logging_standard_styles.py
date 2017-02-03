#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2016 TUNE, Inc. (http://www.tune.com)
#  @namespace logging_mv_integrations
"""
TUNE Multiverse Integration Base
"""

import json
import logging
from string import Template

from logging_mv_integrations.support import (safe_str, safe_int, safe_float)

TUNE_STANDARD_FORMAT_SUPPORTED_KEYS = {
    # 'pathname': {'type': str, 'order': 0, 'label': True},
    # 'lineno': {'type': int, 'order': 1, 'label': True},
    'asctime': {
        'type': None,
        'label': False,
        'order': 2,
        'fmt': '{:30} '
    },
    'levelname': {
        'type': None,
        'label': False,
        'order': 3,
        'fmt': '{:7} '
    },
    'version': {
        'type': str,
        'label': False,
        'order': 4,
        'fmt': '{} '
    },

    #  'memory_total': {'type': None, 'label': False, 'order': 5, 'fmt': '{:>9} '},
    #  'memory_used': {'type': None, 'label': False, 'order': 6, 'fmt': '[{:>9}] '},

    #  'integration_name': {'type': str, 'label': False, 'order': 7},
    #  'integration_version': {'type': str, 'label': False, 'order': 7},
    'message': {
        'type': str,
        'label': False,
        'order': 8
    },
    'start_date': {
        'type': str,
        'label': True,
        'order': 10
    },
    'end_date': {
        'type': str,
        'label': True,
        'order': 11
    },
    'data_size': {
        'type': int,
        'label': True,
        'order': 12
    },
    'row_count': {
        'type': int,
        'label': True,
        'order': 13
    },
    'job_row_count': {
        'type': int,
        'label': True,
        'order': 14
    },
    'count': {
        'type': int,
        'label': True,
        'order': 15
    },
    'data': {
        'type': str,
        'label': True,
        'order': 16
    }
}


class LoggingPercentStyle(object):
    """TUNE Logging Percentage Formatting Style
    """
    default_format = '%(message)s'
    asctime_format = '%(asctime)s'
    asctime_search = '%(asctime)'

    def __init__(self, fmt):
        self._fmt = fmt or self.default_format

    def usesTime(self):
        return self._fmt.find(self.asctime_search) >= 0

    def format(self, record):
        fmt_record_items = {}
        for key, meta in TUNE_STANDARD_FORMAT_SUPPORTED_KEYS.items():
            if key in record.__dict__:
                if 'label' in meta and meta['label']:
                    key_lower = str(key).lower()
                    fmt_record_item = "{}: ".format(key_lower)
                else:
                    fmt_record_item = ""

                fmt_record_item.lower()

                if 'fmt' in meta:
                    meta_fmt = meta['fmt']
                else:
                    meta_fmt = '{},'

                try:
                    if meta['type'] == str:
                        fmt_record_item += \
                            "\"{}\", ".format(safe_str(record.__dict__[key]))
                    elif meta['type'] == int:
                        fmt_record_item += \
                            "{:,}, ".format(safe_int(record.__dict__[key]))
                    elif meta['type'] == float:
                        fmt_record_item += \
                            "{0:.2f}, ".format(safe_float(record.__dict__[key]))
                    elif meta['type'] == dict:
                        fmt_record_item += \
                            "{}, ".format(
                                json.loads(
                                    json.dumps(dict(record.__dict__[key]))
                                )
                            )
                    else:
                        fmt_record_item += meta_fmt.format(record.__dict__[key])
                except ValueError as va_ex:
                    fmt_record_item += "{}: '{}'".format(type(record.__dict__[key]).__name__, str(record.__dict__[key]))

                hash = "{0:03d}".format(meta['order'])
                fmt_record_items[hash] = fmt_record_item

        str_fmt_record = ""
        for key in sorted(fmt_record_items.keys()):
            value = fmt_record_items[key]
            str_fmt_record += value

        return str_fmt_record[:-2]


class LoggingStringFormatStyle(LoggingPercentStyle):
    """TUNE Logging String Formatting Style
    """
    default_format = '{message}'
    asctime_format = '{asctime}'
    asctime_search = '{asctime'

    def format(self, record):
        return self._fmt.format(**record.__dict__)


class LoggingStringTemplateStyle(LoggingPercentStyle):
    """TUNE Logging String Formatting Template Style
    """
    default_format = '${message}'
    asctime_format = '${asctime}'
    asctime_search = '${asctime}'

    def __init__(self, fmt):
        self._fmt = fmt or self.default_format
        self._tpl = Template(self._fmt)
        super(LoggingStringTemplateStyle, self).__init__(fmt)

    def usesTime(self):
        fmt = self._fmt
        return fmt.find('$asctime') >= 0 or fmt.find(self.asctime_format) >= 0

    def format(self, record):
        return self._tpl.substitute(**record.__dict__)


logging._STYLES = {
    '%': (LoggingPercentStyle, logging.BASIC_FORMAT),
    '{': (LoggingStringFormatStyle, '{levelname}:{name}:{message}'),
    '$': (LoggingStringTemplateStyle, '${levelname}:${name}:${message}'),
}
