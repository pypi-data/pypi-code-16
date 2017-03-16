#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtNetwork
from . import const
from .reply import Reply
from .message import Message
from .qommand import Qommand


class Qonnection(QtCore.QObject):
    sigConnectedToSpec = QtCore.pyqtSignal()
    sigSpecReplyArrived = QtCore.pyqtSignal(object, object)
    sigError = QtCore.pyqtSignal(str)

    def __init__(self, address, reconnect=True):
        super().__init__()
        self._address = address
        self._connected = False
        self._reconnect = reconnect
        self._connect()

    def _connect(self):
        host, port = self._address
        self._host = host
        try:
            self._port = int(port)
        except ValueError:
            self._searching = True
            self._port = const.SPEC_MIN_PORT
            self._name = port
        else:
            self._name = ''
            self._searching = False
        self._connectToSpec()

    def _connectToSpec(self):
        self._message = Message()
        self._reply = Reply()
        self._command = Qommand(self)
        self._setSocket()
        self._connectSignals()
        self._sock.connectToHost(self._host, self._port)

    def send(self, message):
        s = self._sock.state()
        if s == QtNetwork.QAbstractSocket.ConnectedState:
            self._sock.write(message)
        elif s == QtNetwork.QAbstractSocket.UnconnectedState and not self._connected and not self._searching:
            if self._reconnect:
                self._connectToSpec()
            else:
                self.sigError.emit('Lost connection to {} at {}:{}'.format(self._name, self._host, self._port))
        else:
            self.sigError.emit('Trying to send messages without established connection to {}'.format(self._name))

    def _setSocket(self):
        self._sock = QtNetwork.QTcpSocket(self)
        self._sock.setProxy(QtNetwork.QNetworkProxy(QtNetwork.QNetworkProxy.NoProxy))

    def _connectSignals(self):
        self._sock.connected.connect(self._sayHello)
        self._sock.readyRead.connect(self._readResponse)
        self._sock.disconnected.connect(self._stopConnection)
        self._sock.error.connect(self._serverHasError)

    def _sayHello(self):
        self.send(self._message.hello())

    def _readResponse(self):
        buf = bytes(self._sock.readAll())
        if self._searching and not self._connected:
            for header, answer in self._reply.unpack(buf):
                if header.cmd == const.HELLO_REPLY:
                    if answer == self._name:
                        self._connected = True
                        self._searching = False
                        self._address = self._host, self._port
                        self.sigConnectedToSpec.emit()
                    else:
                        self._port += 1
                        if self._port >= const.SPEC_MAX_PORT:
                            self._connected = False
                            self._searching = False
                            self.sigError.emit('Count not find {} on the host {}'.format(self._name, self._host))
                            return
                        self._connectToSpec()
        else:
            for header, answer in self._reply.unpack(buf):
                if header.cmd == const.HELLO_REPLY:
                    self._connected = True
                    self._searching = False
                    self._name = answer
                    self.sigConnectedToSpec.emit()
                else:
                    self.sigSpecReplyArrived.emit(header, answer)

    def _stopConnection(self):
        self._searching = False
        self._connected = False
        self.sigError.emit('The connection to {} at {}:{} has been stopped'.format(self._name, self._host, self._port))

    def _serverHasError(self):
        self._connected = False
        self._searching = False
        e = self._sock.errorString()
        self.sigError.emit('The server {} at {}:{} has an error: {}'.format(self._name, self._host, self._port, e))

    def close(self):
        self._stopConnection()
        self._sock.close()

    def __repr__(self):
        return '<Qt SpecConnection to {} running at {}:{}>'.format(self._name, self._host, self._port)

    def isConnected(self):
        return (not self._searching and self._connected and
                QtNetwork.QAbstractSocket.ConnectedState == self._sock.state())

    def name(self):
        return self._name

    def message(self):
        return self._message

    def abort(self):
        self.send(self._message.abort())

    def command(self):
        return self._command
