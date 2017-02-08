import time
from datetime import datetime, timedelta
from email import utils

import pytz
from dateutil import parser
from enum import Enum
from pytz import timezone

__author__ = 'Martin Borba - borbamartin@gmail.com'


def parse_timestr(timestr, **kwargs):
    """
    Parse a string in one of the supported formats.
    Wrapper for 'dateutil.parser.parse'. Check wrapped method docstring for further information

    :param timestr:
        A string containing a date/time stamp

    :return:
        Returns a :class:`datetime.datetime` object or, if the
        ``fuzzy_with_tokens`` option is ``True``, returns a tuple, the
        first element being a :class:`datetime.datetime` object, the second
        a tuple containing the fuzzy tokens.

    :raises ValueError:
        Raised for invalid or unknown string format, if the provided
        :class:`tzinfo` is not in a valid format, or if an invalid date
        would be created.

    :raises OverflowError:
        Raised if the parsed date exceeds the largest valid C integer on
        your system.
    """
    return parser.parse(timestr, **kwargs)


def rfc822():
    """
    Get's the current datetime in RFC 822 (GMT) format 
    I.e.: 'Tue, 14 Jun 2016 05:37:51 -0000'

    :return:
        A string representing the current datetime in RFC 822 format
    """
    nowtuple = datetime.now().timetuple()
    nowtimestamp = time.mktime(nowtuple)
    return utils.formatdate(nowtimestamp)


class TimeUnit(Enum):
    """ Accepted values to perform time operations """

    def __str__(self):
        return self.value

    @property
    def value(self):
        return self._name_.lower()

    SECONDS, MINUTES, HOURS, DAYS, WEEKS = range(5)


class DateTimeUtil(object):
    """
    Utilities class to perform time-related operations easily. 

    Default time zone is used in order to be in-sync with the servers.

    Once instanced it stores the date/time data, to access the live date/time
    info use 'stored_time.now()'
    """

    def __init__(self, display_seconds=False, leading_zero=True):
        self._display_seconds = display_seconds
        self._leading_zero = leading_zero
        self.stored_time = None
        self.time_zone = timezone('US/Eastern')
        self.refresh()

    def refresh(self):
        """ Stores the current date/time data """
        self.stored_time = datetime.now(self.time_zone)

    def change_time_zone(self, new_time_zone, update_stored_time=True):
        self.time_zone = timezone(new_time_zone)

        if not self.stored_time.tzinfo:
            self.stored_time = pytz.utc.localize(self.stored_time)

        if update_stored_time:
            self.stored_time = self.stored_time.astimezone(self.time_zone)

    @property
    def hour(self):
        return self._process_leading_zeros(self.stored_time.strftime('%I'))

    @property
    def hour24(self):
        return self._process_leading_zeros(self.stored_time.strftime('%H'))

    @property
    def minute(self):
        return self._process_leading_zeros(str(self.stored_time.minute))

    @property
    def second(self):
        return self._process_leading_zeros(str(self.stored_time.second))

    @property
    def am_pm(self):
        return self.stored_time.strftime('%p').lower()

    @property
    def date(self):
        return self.stored_time.strftime('%Y-%m-%d')

    @property
    def time(self):
        if self._display_seconds:
            stamp = '%I:%M:%S %p'
        else:
            stamp = '%I:%M %p'

        return self.stored_time.strftime(stamp)

    @property
    def time24(self):
        if self._display_seconds:
            stamp = '%H:%M:%S'
        else:
            stamp = '%H:%M'

        return self.stored_time.strftime(stamp)

    @property
    def timestamp(self):
        if self._display_seconds:
            stamp = '%Y-%m-%d %I:%M:%S %p'
        else:
            stamp = '%Y-%m-%d %I:%M %p'

        return self.stored_time.strftime(stamp)

    @property
    def timestamp24(self):
        if self._display_seconds:
            stamp = '%Y-%m-%d %H:%M:%S'
        else:
            stamp = '%Y-%m-%d %H:%M'

        return self.stored_time.strftime(stamp)

    @property
    def epoch(self):
        return int((self.stored_time - datetime(1970,
                                                1,
                                                1,
                                                tzinfo=self.time_zone)).total_seconds())

    def add_time(self, time_unit, amount):
        """
        Adds a specific amount of time to the currently stored time

        :param time_unit:
            A 'datetime_utils.TimeUnit' enum value
        :param amount:
            An integer representing the time unit amount
        :return:
            The new time
        """
        if not isinstance(time_unit, TimeUnit):
            self._raise_type_error()

        self.stored_time = self.stored_time + timedelta(**{time_unit.value: amount})
        return self.stored_time

    def subtract_time(self, time_unit, amount):
        """
        Subtracts a specific amount of time to the currently stored time 

        :param time_unit:
            A 'datetime_utils.TimeUnit' enum value
        :param amount:
            An integer representing the time unit amount
        :return:
            The new time
        """
        if not isinstance(time_unit, TimeUnit):
            self._raise_type_error()

        self.stored_time = self.stored_time - timedelta(**{time_unit.value: amount})
        return self.stored_time

    @staticmethod
    def _raise_type_error():
        raise TypeError('Parameter \'time_unit\' must be of type \'datetime_utils.TimeUnit\'')

    def _process_leading_zeros(self, time_value):
        if self._leading_zero:
            return time_value.zfill(2)
        else:
            return time_value.lstrip('0')
