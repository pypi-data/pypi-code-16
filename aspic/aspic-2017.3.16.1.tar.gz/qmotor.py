#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from .manager import manager
from . import const


class Motor(QtCore.QObject):
    sigConnected = QtCore.pyqtSignal(str)
    sigNewPosition = QtCore.pyqtSignal(str, float)
    sigMoveDone = QtCore.pyqtSignal(str)
    sigLimitHit = QtCore.pyqtSignal(str)
    sigError = QtCore.pyqtSignal(str)

    def __init__(self, address, name):
        super().__init__()
        self._manager = manager
        self._address = address
        self._name = name
        self._position = 0
        self._low_limit = 0
        self._high_limit = 0
        self._on_limit = False
        self._connected = False
        self._moving = False
        self._connect()

    def __repr__(self):
        return 'Qt Motor {} with {}'.format(self._name, self._connection)

    def _connect(self):
        self._connection = self._manager.qonnect(self._address)
        self._message = self._connection.message()
        self._connection.sigConnectedToSpec.connect(self._connectedToSpec)
        self._connection.sigSpecReplyArrived.connect(self._parseReply)
        self._connection.sigError.connect(self._connectionHasError)
        if self._connection.isConnected():
            self._connectedToSpec()

    def _connectionHasError(self, emsg):
        self._connected = False
        self.sigError.emit(emsg)

    def _connectedToSpec(self):
        self._connected = True
        self._connection.send(self._message.motor_register_high_limit_hit(self._name))
        self._connection.send(self._message.motor_register_low_limit_hit(self._name))
        self._connection.send(self._message.motor_register_high_limit(self._name))
        self._connection.send(self._message.motor_register_low_limit(self._name))
        self._connection.send(self._message.motor_register_position(self._name))
        self._connection.send(self._message.motor_register_move_done(self._name))
        self._connection.send(self._message.motor_read_position(self._name))
        self.sigConnected.emit(self._name)

    def _parseReply(self, header, value):
        try:
            device, name, propert = header.name.decode().split('/')
        except ValueError:
            return
        if device != 'motor' or name != self._name or header.cmd not in (const.EVENT, const.REPLY):
            return
        if propert == 'position':
            self._position = value
            self._on_limit = self._position in (self._low_limit, self._high_limit)
            self.sigNewPosition.emit(self._name, self._position)
        elif propert == 'move_done' and value == 0:
            self._on_limit = self._position in (self._low_limit, self._high_limit)
            self._moving = False
            self.sigMoveDone.emit(self._name)
        elif propert == 'move_done' and value != 0:
            self._moving = True
        elif propert in ('high_limit_hit', 'low_limit_hit'):
            self._on_limit = True
        elif propert == 'low_limit':
            self._low_limit = value
        elif propert == 'high_limit':
            self._high_limit = value
        if self._on_limit:
            self.sigLimitHit.emit(self._name)

    def move(self, position):
        if position == self._position:
            return
        self._connection.send(self._message.motor_move(self._name, position))

    def moveRelative(self, position):
        self.move(self._position + position)

    def stop(self):
        self._connection.abort()

    def name(self):
        return self._name

    def position(self):
        return self._position

    def isOnLimit(self):
        return self._on_limit

    def highLimit(self):
        return self._high_limit

    def lowLimit(self):
        return self._low_limit

    def isConnected(self):
        return self._connected

    def connection(self):
        return self._connection

    def manager(self):
        return self._manager

    def isMoving(self):
        return self._moving
