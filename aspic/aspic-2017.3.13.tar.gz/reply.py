#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import const
from .header import Header


class SpecError(Exception):
    pass


class Reply:
    def __init__(self):
        self._serial = -1
        self._buffer = b''
        self._header = None

    def unpack(self, buf):
        self._buffer += buf
        while self._buffer:
            self._unpack_header()
            data = self._unpack_body()
            if data is None:
                raise StopIteration
            data = self._convert_data(data)
            header = self._header
            self._header = None
            yield header, data

    def _unpack_body(self):
        if not self._header or len(self._buffer) < self._header.datalen:
            return
        data = self._buffer[:self._header.datalen-1]
        self._buffer = self._buffer[self._header.datalen:]
        return data

    def _unpack_header(self):
        if self._header or len(self._buffer) < const.HEADER_SIZE:
            return
        self._header = Header()
        self._header.unpack(self._buffer[:const.HEADER_SIZE])
        self._header.name = self._header.name.replace(b'\x00', b'')
        self._buffer = self._buffer[const.HEADER_SIZE:]

    def _convert_data(self, data):
        if self._header.typ in (const.TYPE_STRING, const.TYPE_DOUBLE):
            try:
                data = float(data)
            except ValueError:
                data = data.decode()
            return data
        else:
            return data.decode()
