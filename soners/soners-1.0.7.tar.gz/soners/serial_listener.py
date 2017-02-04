from tornado.ioloop import IOLoop
from tornado.iostream import BaseIOStream
from . import logger

import functools
import serial


class SerialIOStream(BaseIOStream):

    def __init__(self, connection, *args, **kwargs):
        self.connection = connection
        # self.connection.setblocking(False)
        super(SerialIOStream, self).__init__(*args, **kwargs)

    def close_fd(self):
        self.connection.close()
        self.connection = None

    def read_from_fd(self):
        try:
            chunk = self.connection.readline()
        except Exception:
            return None

        return chunk


class SerialListener(object):
    def __init__(self, io_loop=None, max_buffer_size=None,
                 read_chunk_size=None):
        self.io_loop = io_loop
        self.max_buffer_size = max_buffer_size
        self.read_chunk_size = read_chunk_size

    def listen(self, dev="/dev/ttyACM1", baud_rate=9600, timeout=0):
        if self.io_loop is None:
            self.io_loop = IOLoop.current()
        self.dev = dev
        conn = serial.Serial(dev, baud_rate, timeout=timeout)
        conn.nonblocking()
        callback = functools.partial(self._handle_connection, conn)
        self.io_loop.add_handler(conn.fileno(), callback, self.io_loop.READ)

    def handle_stream(self, stream, device):
        raise NotImplementedError()

    def _handle_connection(self, conn, fd, event):
        try:
            stream = SerialIOStream(conn, io_loop=self.io_loop,
                                    max_buffer_size=self.max_buffer_size,
                                    read_chunk_size=self.read_chunk_size)
            future = self.handle_stream(stream, self.dev)
            if future is not None:
                self.io_loop.add_future(future, lambda f: f.result())
        except Exception:
            logger.error("Error in connection callback", exc_info=True)
