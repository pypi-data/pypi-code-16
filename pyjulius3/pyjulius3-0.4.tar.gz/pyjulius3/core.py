# -*- coding: utf-8 -*-
# Copyright 2011-2012 Antoine Bertin <diaoulael@gmail.com>
# Copyright 2017 Martin Bachmann <bachmmar@gmail.com>
#
# This file is part of pyjulius3.
#
# pyjulius is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyjulius is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pyjulius3.  If not, see <http://www.gnu.org/licenses/>.
from .exceptions import ConnectionError
from .models import Sentence
from xml.etree.ElementTree import XML, ParseError
import queue
import logging
import re
import socket
import threading


__all__ = ['CONNECTED', 'DISCONNECTED', 'Client']
logger = logging.getLogger(__name__)


#: Connected client state
CONNECTED = 1

#: Disconnected client state
DISCONNECTED = 2


class Client(threading.Thread):
    """Threaded Client to connect to a julius module server

    :param string host: host of the server
    :param integer port: port of the server
    :param string encoding: encoding to use to decode socket's output
    :param boolean modelize: try to interpret raw xml :class:`~xml.etree.ElementTree.Element` as :mod:`~pyjulius.models` if ``True``

    .. attribute:: host

        Host of the server

    .. attribute:: port

        Port of the server

    .. attribute:: encoding

        Encoding to use to decode socket's output

    .. attribute:: modelize

        Try to interpret raw xml :class:`~xml.etree.ElementTree.Element` as :mod:`~pyjulius.models` if ``True``

    .. attribute:: results

        Results received when listening to the server. This :class:`~queue.queue` is filled with
        raw xml :class:`~xml.etree.ElementTree.Element` objects and :class:`~pyjulius.models` (if :attr:`modelize`)

    .. attribute:: sock

        The socket used

    .. attribute:: state

        Current state. State can be:

        * :data:`~pyjulius.core.CONNECTED`
        * :data:`~pyjulius.core.DISCONNECTED`

    """
    def __init__(self, host='localhost', port=10500, encoding='utf-8', modelize=True):
        super(Client, self).__init__()
        self.host = host
        self.port = port
        self.encoding = encoding
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.state = DISCONNECTED
        self._stop = False
        self.results = queue.Queue()
        self.modelize = modelize
        self.socket_file = self.sock.makefile(mode='r', encoding=self.encoding)

    def stop(self):
        """Stop the thread"""
        self._stop = True

    def run(self):
        """Start listening to the server"""
        logger.info(u'Started listening')
        while not self._stop:
            xml = self._readxml()

            # Exit on invalid XML
            if xml is None:
                break

            # Raw xml only
            if not self.modelize:
                logger.info(u'Raw xml: %s' % xml)
                self.results.put(xml)
                continue

            # Model objects + raw xml as fallback
            if xml.tag == 'RECOGOUT':
                sentence = Sentence.from_shypo(xml.find('SHYPO'), self.encoding)
                logger.info(u'Modelized recognition: %r' % sentence)
                self.results.put(sentence)
            else:
                logger.info(u'Unmodelized xml: %s' % xml)
                self.results.put(xml)

        logger.info(u'Stopped listening')

    def connect(self):
        """Connect to the server

        :raise ConnectionError: If socket cannot establish a connection

        """
        try:
            logger.info(u'Connecting %s:%d' % (self.host, self.port))
            self.sock.connect((self.host, self.port))
        except socket.error:
            raise ConnectionError()

        self.state = CONNECTED

    def disconnect(self):
        """Disconnect from the server"""
        logger.info(u'Disconnecting...')
        self.stop()  # stops the thread
        self.sock.shutdown(socket.SHUT_RDWR) # enforces the socket file to interrupt reading
        self.sock.close()
        # self.join()  # wait for the thread to die does not work
        self.socket_file.close()
        self.state = DISCONNECTED
        logger.info(u'Disconnected')

    def send(self, command, timeout=5):
        """Send a command to the server

        :param string command: command to send

        """
        logger.info(u'Sending %s' % command)
        self.sock.makefile(mode='w').writelines(command)

    def _readblock(self):
        """Read a block from the server. Lines are read until a character ``.`` is found

        :return: the read block
        :rtype: string

        """
        block = ''
        while not self._stop:
            line = self.socket_file.readline()
            if '.' in line and len(line) <= 2:
                break
            block += line

        return block

    def _readxml(self):
        """Read a block and return the result as XML

        :return: block as xml
        :rtype: xml.etree.ElementTree

        """
        block = re.sub(r'<(/?)s>', r'&lt;\1s&gt;', self._readblock())
        try:
            xml = XML(block)
        except ParseError:
            xml = None
        return xml
