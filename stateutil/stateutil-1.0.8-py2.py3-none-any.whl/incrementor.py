#!/usr/bin/env python
# encoding: utf-8

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'


class Incrementor(object):

    def __init__(self,
                 start_value=0):
        self.__start_value = start_value
        self.__max = start_value
        self.set(start_value)

    def prev(self):
        self.__count -= 1
        return self.__count

    def previous(self):
        return self.prev()

    def __set_max(self):
        if self.__count > self.__max:
            self.__max = self.__count

    def set(self,
            value):
        self.__count = value
        self.__set_max()

    @property
    def max(self):
        return self.__max

    def next(self):
        self.__count += 1
        self.__set_max()
        return self.__count

    def start(self):
        self.__count = self.__start_value
        return self.__count

    @property
    def current(self):
        return self.__count
