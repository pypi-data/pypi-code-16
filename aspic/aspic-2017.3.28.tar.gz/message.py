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

    def _pack_header(self, cmd, datalen=0, name='', typ=const.TYPE_STRING):
        self._serial += 1
        h = LHeader()
        packed = h.pack(self._serial, cmd, typ, datalen, name)
        return packed

    def _pack_data(self, data):
        return b'%s\x00' % str(data).encode(encoding='ascii', errors='ignore')

    def _register(self, name='', datalen=0, *, typ=const.TYPE_STRING):
        return self._pack_header(const.REGISTER, datalen, name, typ)

    def _read(self, name='', datalen=0, *, typ=const.TYPE_STRING):
        return self._pack_header(const.CHAN_READ, datalen, name, typ)

    def _send(self, name='', datalen=0, *, typ=const.TYPE_STRING):
        return self._pack_header(const.CHAN_SEND, datalen, name, typ)

    def hello(self):
        return self._pack_header(const.HELLO, name='python')

    def abort(self):
        return self._pack_header(const.ABORT, )

    def motor_register_position(self, name):
        return self._register('motor/{}/position'.format(name))

    def motor_register_high_limit_hit(self, name):
        return self._register('motor/{}/high_limit_hit'.format(name))

    def motor_register_low_limit_hit(self, name):
        return self._register('motor/{}/low_limit_hit'.format(name))

    def motor_register_high_limit(self, name):
        return self._register('motor/{}/high_limit'.format(name))

    def motor_register_low_limit(self, name):
        return self._register('motor/{}/low_limit'.format(name))

    def motor_register_move_done(self, name):
        return self._register('motor/{}/move_done'.format(name))

    def motor_register_dial_position(self, name):
        return self._register('motor/{}/dial_position'.format(name))

    def motor_register_offset(self, name):
        return self._register('motor/{}/offset'.format(name))

    def motor_register_unusable(self, name):
        return self._register('motor/{}/unusable'.format(name))

    def motor_register_slew_rate(self, name):
        return self._register('motor/{}/slew_rate'.format(name))

    def motor_register_step_size(self, name):
        return self._register('motor/{}/step_size'.format(name))

    def motor_read_position(self, name):
        return self._read('motor/{}/position'.format(name))

    def motor_read_unusable(self, name):
        return self._read('motor/{}/unusable'.format(name))

    def motor_move(self, name, position):
        data = self._pack_data(position)
        header = self._send('motor/{}/start_one'.format(name), len(data))
        return header + data

    def motor_set_offset(self, name, offset):
        data = self._pack_data(offset)
        header = self._send('motor/{}/offset'.format(name), len(data))
        return header + data

    def motor_set_slew_rate(self, name, slew):
        data = self._pack_data(slew)
        header = self._send('motor/{}/slew_rate'.format(name), len(data))
        return header + data

    def counter_register(self, name):
        return self._register('scaler/{}/value'.format(name))

    def counter_read(self, name):
        return self._read('scaler/{}/value'.format(name))

    def counter_count(self, name, sec):
        data = self._pack_data(sec)
        header = self._send('scaler/{}/count'.format(name), len(data))
        return header + data

    def command_run(self, command):
        data = self._pack_data(command)
        header = self._pack_header(const.CMD_WITH_RETURN, len(data))
        return header + data

    def command_register(self):
        return self._register('status/ready')
