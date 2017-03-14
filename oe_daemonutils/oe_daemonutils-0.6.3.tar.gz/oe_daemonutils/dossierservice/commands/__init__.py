# -*- coding: utf-8 -*-
import abc


class BasicCommand(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def execute(self, *args, **kwargs):
        raise NotImplementedError('Implementations should override the execute method')
