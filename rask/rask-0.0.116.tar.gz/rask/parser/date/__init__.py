import arrow
from calendar import timegm
from datetime import datetime

__all__ = [
    'datetime_float',
    'datetime_float_str',
    'datetime2timestamp',
    'timestamp2datetime'
]

def datetime_float():
    return arrow.utcnow().float_timestamp

def datetime_float_str():
    return str(datetime_float())

def datetime2timestamp(arg):
    return timegm(arg.timetuple()) + arg.microsecond/1e6

def timestamp2datetime(arg):
    return datetime.fromtimestamp(int(arg))
