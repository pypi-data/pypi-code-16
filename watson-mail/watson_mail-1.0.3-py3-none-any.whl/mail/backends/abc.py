# -*- coding: utf-8 -*-
import abc


class Base(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def send(self, message):
        raise NotImplementedError('send must be implemented')
