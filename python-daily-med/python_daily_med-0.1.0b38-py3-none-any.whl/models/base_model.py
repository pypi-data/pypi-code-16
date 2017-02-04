# -*- coding: utf-8 -*-
# Copyright 2017-TODAY LasLabs Inc.
# License MIT (https://opensource.org/licenses/MIT).

from datetime import date, datetime


class BaseModel(dict):
    """ BaseModel provides a core for all model objects. """

    DATE_FMT = '%b %d, %Y'

    def __str__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join(['%s=%s' % (k, v) for k, v in self.items()]),
        )

    def __repr__(self):
        return self.__str__()

    def str_to_date(self, date_str):
        """ str_to_date returns a date obj representing date_str. """
        dt = datetime.strptime(date_str, self.DATE_FMT)
        return date(dt.year, dt.month, dt.day)

    def date_to_str(self, date_obj):
        """ date_to_str returns a str representation of the date. """
        return date_obj.strftime(self.DATE_FMT)
