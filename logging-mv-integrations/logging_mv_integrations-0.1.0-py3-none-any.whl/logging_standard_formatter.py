#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2016 TUNE, Inc. (http://www.tune.com)
#  @namespace logging_mv_integrations
"""
TUNE Multiverse Integration Base
"""

import datetime as dt
import tzlocal
import coloredlogs


class LoggingStandardFormatter(coloredlogs.ColoredFormatter):
    def converter(self, timestamp):
        tz = tzlocal.get_localzone()
        return dt.datetime.fromtimestamp(timestamp, tz)

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            return ct.strftime(datefmt)
        else:
            return ct.strftime("%Y-%m-%d %H:%M:%S %z")
