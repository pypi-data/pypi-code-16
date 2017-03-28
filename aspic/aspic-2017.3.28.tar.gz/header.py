#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import ctypes
from . import const


class _Header:
    _fields_ = [
        ('magic', ctypes.c_uint32),
        ('header', ctypes.c_int32),
        ('size', ctypes.c_uint32),
        ('id', ctypes.c_uint32),
        ('sec', ctypes.c_uint32),
        ('usec', ctypes.c_uint32),
        ('cmd', ctypes.c_int32),
        ('typ', ctypes.c_int32),
        ('rows', ctypes.c_uint32),
        ('cols', ctypes.c_uint32),
        ('datalen', ctypes.c_uint32),
        ('error', ctypes.c_int32),
        ('flags', ctypes.c_int32),
        ('name', ctypes.c_char * 80)
    ]

    def pack(self, serial, cmd, typ, datalen, name):
        timestamp = time.time()
        self.magic = const.MAGIC_NUMBER
        self.header = const.NATIVE_HEADER_VERSION
        self.size = const.HEADER_SIZE
        self.id = serial
        self.sec = int(timestamp)
        self.usec = int((timestamp - self.sec) * 1e6)
        self.cmd = cmd
        self.typ = typ
        self.datalen = datalen
        self.name = name.encode()
        self.error = 0
        return bytes(self)

    def unpack(self, buffer):
        ctypes.memmove(ctypes.addressof(self), buffer, const.HEADER_SIZE)
        return self

    def __repr__(self):
        try:
            return ('<Spec header: size={:d}, id={:d}, cmd={:d}, type={:d}, datalen={:d}, error={:d}, name={}'
                    ''.format(self.size, self.id, self.cmd, self.typ, self.datalen, self.error, self.name))
        except AttributeError:
            return ''


class LHeader(ctypes.LittleEndianStructure):
    _fields_ = _Header._fields_
    pack = _Header.pack
    unpack = _Header.unpack
    __repr__ = _Header.__repr__


class BHeader(ctypes.BigEndianStructure):
    _fields_ = _Header._fields_
    pack = _Header.pack
    unpack = _Header.unpack
    __repr__ = _Header.__repr__


Header = LHeader
