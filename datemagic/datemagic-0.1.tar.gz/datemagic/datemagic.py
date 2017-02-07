#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

# default chunk size in days
DEFAULT_CHUNK_SIZE = 30


def split_interval_int(startmonth, startday, startyear,
                       endmonth=None, endday=None, endyear=None,
                       chunksize=DEFAULT_CHUNK_SIZE):
    """ Splits the date interval into chunks

    Dates are specified by 6 int values.  This is convenience function ---
    it is a wrapper around :py:func:interval_split.

    :param int startmonth: start month
    :param int startday: start day
    :param int startyear: start year
    :param int endmonth: end month
    :param int endday: end day
    :param int endyear: end year
    :param int chunksize: size of a single time chunk in days.  Default
        chunk size is 30 days.

    :return: list of tuples
    :rtype: list

    """
    date_start = datetime.date(startyear, startmonth, startday)
    if (endmonth is None or
            endday is None or
            endyear is None):
        date_end = None
    else:
        date_end = datetime.date(endyear, endmonth, endday)
    return split_interval(date_start, date_end, chunksize)


def split_interval(date_start, date_end=None,
                   chunksize=DEFAULT_CHUNK_SIZE):
    """ Splits the date interval into chunks of `chunksize` size.

    Splits the time interval between the start and end dates into chunks
    returning a list of datetime.date tuples.

    :param datetime.date date_start: start date
    :param datetime.date date_end: end date
    :param int chunksize: size of a single time chunk in days.  Default
        chunk size is 30 days.
    :return: list of tuples
    :rtype: list
    """
    if date_end is None:
        date_end = datetime.datetime.now().date()
    if date_start > date_end:
        date_start, date_end = [date_end, date_start]
    dt = datetime.timedelta(chunksize)
    retval = list()
    # ---- calculations
    num_days = (date_end - date_start).days
    assert num_days >= 0
    while num_days >= 0:
        end_dt = (dt - datetime.timedelta(1) if num_days >= chunksize
                  else datetime.timedelta(num_days))
        date_end = date_start + end_dt
        retval.append((date_start, date_end,))
        date_start += dt
        num_days -= chunksize

    return retval
