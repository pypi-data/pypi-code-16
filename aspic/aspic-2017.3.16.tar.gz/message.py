#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import const
from .header import LHeader


class Message:
    def __init__(self):
        self._serial = -1

    @property
    def serial(self):
        return self._serial

    @serial.setter
    def serial(self, serial):
        self._serial = serial

    def _pack_header(self, cmd, datalen=0, name='', *, typ=const.TYPE_STRING):
        self._serial += 1
        h = LHeader()
        packed = h.pack(self._serial, cmd, typ, datalen, name)
        return packed

    def _pack_data(self, data):
        return b'%s\x00' % str(data).encode(encoding='ascii', errors='ignore')

    def hello(self):
        return self._pack_header(const.HELLO, name='python')

    def abort(self):
        return self._pack_header(const.ABORT)

    def motor_register_position(self, name):
        s = 'motor/{}/position'.format(name)
        return self._pack_header(const.REGISTER, name=s)

    def motor_register_high_limit_hit(self, name):
        s = 'motor/{}/high_limit_hit'.format(name)
        return self._pack_header(const.REGISTER, name=s)

    def motor_register_low_limit_hit(self, name):
        s = 'motor/{}/low_limit_hit'.format(name)
        return self._pack_header(const.REGISTER, name=s)

    def motor_register_high_limit(self, name):
        s = 'motor/{}/high_limit'.format(name)
        return self._pack_header(const.REGISTER, name=s)

    def motor_register_low_limit(self, name):
        s = 'motor/{}/low_limit'.format(name)
        return self._pack_header(const.REGISTER, name=s)

    def motor_register_move_done(self, name):
        s = 'motor/{}/move_done'.format(name)
        return self._pack_header(const.REGISTER, name=s)

    def motor_read_position(self, name):
        s = 'motor/{}/position'.format(name)
        return self._pack_header(const.CHAN_READ, name=s)

    def motor_move(self, name, position):
        data = self._pack_data(position)
        s = 'motor/{}/start_one'.format(name)
        header = self._pack_header(const.CHAN_SEND, len(data), s)
        return header + data

    def counter_register(self, name):
        s = 'scaler/{}/value'.format(name)
        return self._pack_header(const.REGISTER, name=s)

    def counter_read(self, name):
        s = 'scaler/{}/value'.format(name)
        return self._pack_header(const.CHAN_READ, name=s)

    def counter_count(self, name, sec):
        data = self._pack_data(sec)
        s = 'scaler/{}/count'.format(name)
        header = self._pack_header(const.CHAN_SEND, len(data), s)
        return header + data

    def command_run(self, command):
        data = self._pack_data(command)
        header = self._pack_header(const.CMD_WITH_RETURN, len(data))
        return header + data

    def command_register(self):
        s = 'status/ready'
        header = self._pack_header(const.REGISTER, name=s)
        return header
