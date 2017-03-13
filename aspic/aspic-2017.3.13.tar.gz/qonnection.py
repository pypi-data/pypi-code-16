#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtNetwork
from . import const, excepts
from .reply import Reply
from .message import Message


class Qonnection(QtCore.QObject):
    sigConnectedToSpec = QtCore.pyqtSignal()
    sigSpecReplyArrived = QtCore.pyqtSignal(object, object)

    def __init__(self, address):
        super().__init__()
        self._address = address
        self._connected = False
        self._connect()

    def _connect(self):
        host, port = self._address
        self._host = host
        try:
            self._port = int(port)
        except ValueError:
            self._searching = True
            self._port = const.SPEC_MIN_PORT
            self.name = port
        else:
            self.name = ''
            self._searching = False
        self._connectToSpec()

    def _connectToSpec(self):
        self.message = Message()
        self._reply = Reply()
        self._setSocket()
        self._connectSignals()
        self._sock.connectToHost(self._host, self._port)

    def send(self, message):
        self._sock.write(message)

    def _setSocket(self):
        self._sock = QtNetwork.QTcpSocket(self)
        self._sock.setProxy(QtNetwork.QNetworkProxy(QtNetwork.QNetworkProxy.NoProxy))

    def _connectSignals(self):
        self._sock.connected.connect(self._sayHello)
        self._sock.readyRead.connect(self._readResponse)
        self._sock.disconnected.connect(self._stopConnection)
        self._sock.error.connect(self._serverHasError)

    def _sayHello(self):
        self.send(self.message.hello())

    def _readResponse(self):
        buf = bytes(self._sock.readAll())
        if self._searching and not self._connected:
            for header, answer in self._reply.unpack(buf):
                if header.cmd == const.HELLO_REPLY:
                    if answer == self.name:
                        self._searching = False
                        self._connected = True
                        self.sigConnectedToSpec.emit()
                    else:
                        self._port += 1
                        if self._port >= const.SPEC_MAX_PORT:
                            raise excepts.SpecConnectionError('Could not find Spec session {}'.format(self.name))
                        self._connectToSpec()
        else:
            for header, answer in self._reply.unpack(buf):
                if header.cmd == const.HELLO_REPLY:
                    self._connected = True
                    self._searching = False
                    self.name = answer
                    self.sigConnectedToSpec.emit()
                else:
                    self.sigSpecReplyArrived.emit(header, answer)

    def _stopConnection(self):
        self._searching = False
        self._connected = False

    def _serverHasError(self):
        self._searching = False
        self._connected = False

    def close(self):
        self._stopConnection()
        self._sock.close()

    def __repr__(self):
        return '<Qt SpecConnection to {} running at {}:{}>'.format(self.name, self._host, self._port)
