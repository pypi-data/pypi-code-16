# -*- coding: utf-8 -*-

from datetime import datetime, timedelta


class PyBrDST():

    def easter_date(self, year):
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        L = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * L) // 451
        month = (h + L - 7 * m + 114) // 31
        day = ((h + L - 7 * m + 114) % 31) + 1
        return datetime(year, month, day)

    def carnival_date(self, easter_day):
        return easter_day - timedelta(days=47)

    def begin_dst(self, year):
        diff = 6 - datetime(year, 10, 1).weekday()
        return datetime(year, 10, 1) + timedelta(days=diff + 14)

    def end_dst(self, year):
        diff = 6 - datetime(year, 2, 1).weekday()
        end_stime = datetime(year, 2, 1) + timedelta(days=diff + 14)
        if self.carnival_date(self.easter_date(year)) == end_stime:
            return end_stime + timedelta(days=7)
        return end_stime

    def get_dst(self, year):
        return (self.begin_dst(year), self.end_dst(year + 1))
