#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from .manager import manager
from . import const


class Motor(QtCore.QObject):
    sigMotorConnected = QtCore.pyqtSignal()
    sigMotorPosition = QtCore.pyqtSignal(str, float)

    def __init__(self, address, name):
        super().__init__()
        self._manager = manager
        self._address = address
        self.name = name
        self._position = 0
        self._connected = False
        self._connect()

    def __repr__(self):
        return 'Qt Motor {} with {}'.format(self.name, self._connection)

    def _connect(self):
        self._connection = self._manager.qonnect(self._address)
        self._message = self._connection.message
        self._connection.sigConnectedToSpec.connect(self._connectedToSpec)
        self._connection.sigSpecReplyArrived.connect(self._parseReply)

    def _connectedToSpec(self):
        self._connected = True
        self.sigMotorConnected.emit()
        self._connection.send(self._message.motor_register_position(self.name))
        self._connection.send(self._message.motor_read_position(self.name))

    def _parseReply(self, header, value):
        device, name, propert = header.name.decode().split('/')
        if device != 'motor' or name != self.name:
            return
        if header.cmd in (const.EVENT, const.REPLY) and propert == 'position':
            self._position = value
            self.sigMotorPosition.emit(self.name, self._position)
