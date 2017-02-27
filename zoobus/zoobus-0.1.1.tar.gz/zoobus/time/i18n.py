# coding=utf8

import pytz
import time
import datetime


def get_local_today(self, timezone):
    """
    >>> get_local_today("Asia/Shanghai")
    :param self:
    :param timezone:
    :return:
    """
    tz = pytz.timezone(timezone)
    now = datetime.datetime.now()
    offset = int(tz.utcoffset(now).total_seconds() / 3600.0)
    offset += time.timezone / 3600.0
    market_today = now + datetime.timedelta(hours=offset)
    market_today = market_today.date()
    return market_today
