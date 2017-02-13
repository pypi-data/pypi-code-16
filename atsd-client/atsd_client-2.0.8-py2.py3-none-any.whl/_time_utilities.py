import time
import copy
import dateutil.parser
import calendar
from datetime import datetime
from dateutil.tz import tzlocal, tzutc
import numbers
try:
    unicode = unicode
except NameError:
    unicode = str

def _current_aware_datetime():
    return datetime.now(tzlocal())

def _current_aware_timestring():
    return str(datetime.now(tzlocal()).replace(microsecond=0).isoformat())

def _iso_to_milliseconds(time_string):
    """
    :param time_string: in iso 8601 format'
    :return: timestamp in milliseconds
    """
    utc_dt = dateutil.parser.parse(time_string)
    return calendar.timegm(utc_dt.timetuple()) * 1000


def _dt_to_utc(datetime_obj):
    """
    :param datetime_obj: datetime object'
    :return: datetime instance
    """
    if datetime_obj.tzinfo is None:
        return datetime_obj.replace(tzinfo=tzlocal()).astimezone(tzutc())
    else:
        return datetime_obj.astimezone(tzutc())

def to_timestamp(time):
    """
    :param time: None | `str` in iso format | :class:`datetime` | `int`
    :return: timestamp in milliseconds
    """
    return _iso_to_milliseconds(to_iso_utc(time))

def to_iso_utc(time):
    """
    :param time: None | iso `str` | :class:`datetime` | `int`
    :return: timestamp in milliseconds
    """
    aux_time = None
    if time is None:
        aux_time = _current_aware_datetime()
    if isinstance(time, (str, unicode)):
        try:
            aux_time = dateutil.parser.parse(time)
        except ValueError:
            return time
    elif isinstance(time, datetime):
        aux_time = time
    elif isinstance(time, numbers.Number):
        aux_time = datetime.utcfromtimestamp(time * 0.001).replace(tzinfo=tzutc()) # expecting milliseconds
    elif aux_time is None:
        raise ValueError('data "time" should be either number, datetime instance, None or str')
    return str(_dt_to_utc(aux_time).replace(microsecond=0).isoformat())
