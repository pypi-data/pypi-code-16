# The MIT License (MIT)
#
# Copyright (c) 2016,Christoph Paulik
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
Tests for the dates module.
'''

import datedown.dates as dt
from datetime import datetime


def test_10_hourly():

    start = datetime(2000, 2, 28)
    end = datetime(2000, 3, 1)
    steps = list(dt.n_hourly(start, end, 10))
    steps_should = [datetime(2000, 2, 28),
                    datetime(2000, 2, 28, 10, 0),
                    datetime(2000, 2, 28, 20, 0),
                    datetime(2000, 2, 29, 6, 0),
                    datetime(2000, 2, 29, 16, 0)]
    assert steps == steps_should


def test_hourly():

    start = datetime(2000, 2, 28, 23)
    end = datetime(2000, 2, 29, 5)
    steps = list(dt.hourly(start, end))
    steps_should = [datetime(2000, 2, 28, 23),
                    datetime(2000, 2, 29, 0),
                    datetime(2000, 2, 29, 1),
                    datetime(2000, 2, 29, 2),
                    datetime(2000, 2, 29, 3),
                    datetime(2000, 2, 29, 4),
                    datetime(2000, 2, 29, 5)]
    assert steps == steps_should


def test_2_daily():

    start = datetime(2000, 2, 27)
    end = datetime(2000, 3, 4)
    steps = list(dt.n_daily(start, end, 2))
    steps_should = [datetime(2000, 2, 27),
                    datetime(2000, 2, 29),
                    datetime(2000, 3, 2),
                    datetime(2000, 3, 4)]
    assert steps == steps_should


def test_daily():

    start = datetime(2000, 2, 27)
    end = datetime(2000, 3, 2)
    steps = list(dt.daily(start, end))
    steps_should = [datetime(2000, 2, 27),
                    datetime(2000, 2, 28),
                    datetime(2000, 2, 29),
                    datetime(2000, 3, 1),
                    datetime(2000, 3, 2)]
    assert steps == steps_should
