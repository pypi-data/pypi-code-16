#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import const
from .header import Header


class Message:
    def __init__(self):
        self._serial = -1

    @property
    def serial(self):
        return self._serial

    @serial.setter
    def serial(self, serial):
        self._serial = serial

    def _pack_header(self, cmd, typ, datalen, name):
        self._serial += 1
        h = Header()
        packed = h.pack(self._serial, cmd, typ, datalen, name)
        return packed

    def hello(self):
        return self._pack_header(const.HELLO, const.TYPE_STRING, 0, 'python')

    def motor_register_position(self, name):
        s = 'motor/{}/position'.format(name)
        return self._pack_header(const.REGISTER, const.TYPE_STRING, 0, s)

    def motor_read_position(self, name):
        s = 'motor/{}/position'.format(name)
        return self._pack_header(const.CHAN_READ, const.TYPE_STRING, 0, s)
