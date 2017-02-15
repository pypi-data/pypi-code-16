#!/usr/bin/env python
# -*-coding:utf-8-*-

import datetime
import gevent.greenlet


def now():
    """  A non-tz-aware now  """
    return datetime.datetime.now()

def now_str():
    return now().strftime('%Y-%m-%d %H:%M:%S')

def format_time(timeinfo):
    return datetime.datetime.fromtimestamp(timeinfo).strftime('%Y-%m-%d %H:%M:%S')


class Ticker(gevent.greenlet.Greenlet):
    def __init__(self, period, callback, *args, **kwargs):
        super(Ticker, self).__init__(*args, **kwargs)
        self._period = period
        self._callback = callback
        self._complete = gevent.event.Event()

    def stop(self):
        self._complete.set()

    def _run(self):
        while not self._complete.is_set():
            self._callback()
            self._complete.wait(self._period)

