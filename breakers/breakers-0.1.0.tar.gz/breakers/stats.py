# -*- coding: utf-8 -*-

"""
breakers.stats
~~~~~~~~~~~~~~

Metrics for tracking Circuit Breaker status.

:Example:

>>> m = Stats(10000)
>>> m.add(1)
>>> print(m.get())
"""

import collections
from .utils import ms_now


class Stats(object):
    """A dynamic rolling window for tracking events happened in the near past

    :param time_span: time interval the rolling window tracks in milliseconds
    :param unit: the unit the interval split into
    """
    def __init__(self, time_span, unit=1000):
        self._time_span = time_span
        self._unit = unit
        self._buckets = collections.deque(maxlen=int(time_span / unit))

    def _get_last_bucket(self):
        """Get the latest bucket

        This function will roll the window.
        """
        t = ms_now()
        if not self._buckets:
            self._buckets.appendleft(_Bucket(t))

        for _ in range(self._buckets.maxlen):
            b = self._buckets[0]
            end = b.created_at + self._unit

            if t - end < 0:
                return b

            # Expired
            if t - end > self._time_span:
                self._buckets.clear()
                return self._get_last_bucket()

            self._buckets.appendleft(_Bucket(end))

        return self._buckets[0]

    def add(self, value):
        """Add value to the window

        We always add value to the latest bucket. The definition of latest
        bucket:

            current_time - latest.created_at < unit

        :param value: the value to add
        """
        self._get_last_bucket().add(value)

    def get(self):
        """Get total stats of the window

        The result is the sum of the values of all the buckets.
        """
        # Roll the buckets
        self._get_last_bucket()
        return sum(b.value for b in self._buckets)


class _Bucket(object):
    def __init__(self, created_at):
        self.created_at = created_at
        self.value = 0

    def add(self, value):
        self.value += value
