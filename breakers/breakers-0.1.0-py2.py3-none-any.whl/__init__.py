# -*- coding: utf-8 -*-

"""
breakers
~~~~~~~~

Usable Circuit Breaker pattern implementation.

:Example:

>>> breaker = Breaker()
>>> breaker.is_allow()
>>> breaker.add_success(value)
>>> breaker.add_failure(value)
"""

from .stats import Stats
from .utils import ms_now

try:
    from enum import Enum
except ImportError:
    class Enum(object):
        pass


class BreakerStatus(Enum):
    OPEN = 1
    CLOSED = 2


class Breaker(object):
    """Circuit Breaker for tesing allowance to call the function

    :param time_span: time interval for tracking function calls, milliseconds
    :param unit: the unit the time span split into, milliseconds
    :param calls_limit: the function call limit
    :param error_limit: error rates limit
    :param retry_time: time interval to try a single call when the breaker open
                       in milliseconds
    """

    def __init__(self, time_span=20000, unit=1000, calls_limit=10,
                 error_limit=0.5, retry_time=10000):
        self._metrics = {
            'success': Stats(time_span, unit),
            'failure': Stats(time_span, unit)
        }
        self.calls_limit = calls_limit
        self.error_limit = error_limit
        self.retry_time = retry_time
        self._status = BreakerStatus.CLOSED
        self._when_open = 0

    def is_allow(self):
        """Whether it's allowd to call the protected function
        """
        is_open = self.is_open()
        if not is_open:
            return True
        now = ms_now()
        if now > self._when_open + self.retry_time:
            self._when_open = now
            return True
        return False

    def is_open(self):
        """Test the breaker is open or not
        """
        if self._status == BreakerStatus.OPEN:
            return True

        if self.calls < self.calls_limit or \
                self.error_rates < self.error_limit:
            return False

        # Trip the breaker
        self._status = BreakerStatus.OPEN
        self._when_open = ms_now()
        return True

    def add_success(self, value):
        """Increase the success metric

        :param value: the value to increase
        """
        if self._status == BreakerStatus.OPEN:
            # Function call succeed, close the breaker.
            self._status = BreakerStatus.CLOSED

        self._metrics['success'].add(value)

    def add_failure(self, value):
        """Increase the failure metric

        :param value: the value to increase
        """
        self._metrics['failure'].add(value)

    @property
    def calls(self):
        return sum(s.get() for s in self._metrics.values())

    @property
    def error_rates(self):
        failure = self._metrics['failure'].get()
        success = self._metrics['success'].get()
        total = float(failure + success)
        return failure / total if total else 0
