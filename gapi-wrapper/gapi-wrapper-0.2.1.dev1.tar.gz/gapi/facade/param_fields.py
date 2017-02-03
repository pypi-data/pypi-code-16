# -*- coding: utf-8 -*-


class FacadeParam(object):

    def __init__(self):
        self._value = None

    def validate(self):
        pass

    @property
    def value(self):
        return self._value


class AdGroupFieldsCases(FacadeParam):
    pass

