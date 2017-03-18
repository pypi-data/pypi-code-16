"""
chitchat.connection
~~~~~~~~~~~~~~~~~~~

This module contains the asynchronous connection class used to connect to an IRC server.
"""

from asyncio import get_event_loop, open_connection
from functools import wraps

from .exceptions import ConnectionNotOpen
from .utils import nameof


def error_if_connection_closed(func, error_type=ConnectionNotOpen):

    @wraps(func)
    async def method(self, *args, **kwargs):
        if not self.connected:
            raise error_type

        return (await func(self, *args, **kwargs))

    return method



class Connection:
    """
    Interface that wraps a StreamReader and StreamWriter.

    >>> async with Connection('irc.chitchat.com', 6667) as conn:
    ...     async for line in conn:
    ...         conn.loop.call_soon(print, line)
    ...
    b':irc.chitchat.com 439 * :Please wait while we process your connection.\r\n'
    [...]
    b'ERROR :Closing Link: irc.chitchat.com (Registration timed out)\r\n'

    >>> conn = Connection('irc.chitchat.com', 6667)
    >>> await conn.open()
    >>> async for line in conn:
    ...     conn.loop.call_soon(print, line)
    ...
    b':irc.rizon.net 439 * :Please wait while we process your connection.\r\n'
    [...]
    b'ERROR :Closing Link: irc.chitchat.com (Registration timed out)\r\n'
    >>> await conn.close()
    """

    def __init__(self, host, port, *, loop=None, **options):
        self.host = host
        self.port = port
        self._loop = loop or get_event_loop()
        self.options = options

        self.reader, self.writer = None, None


    @property
    def loop(self):
        """Read-only event loop."""
        return self._loop


    @property
    def connected(self):
        """Read-only connection status."""
        if not (self.reader and self.writer):
            return False

        # if reader or writer have received EOF then we've disconnected
        return (not self.reader.at_eof()) and (not self.writer.transport.is_closing())


    async def open(self):
        """
        Open a connection to `self.host`.
        """
        streams = await open_connection(
            self.host,
            self.port,
            loop=self.loop,
            **self.options,
        )
        self.reader, self.writer = streams

        return streams


    async def close(self):
        reader, writer = self.reader, self.writer

        if not reader.at_eof():
            reader.feed_eof()

        await reader.read()

        if writer.can_write_eof():
            writer.write_eof()

        writer.close()


    async def __aenter__(self):
        if not self.connected:
            await self.open()

        return self


    async def __aexit__(self, type, value, tb):
        if self.connected:
            await self.close()

        # do not suppress propagation of exceptions
        return False


    def __aiter__(self):
        return self


    async def __anext__(self):
        val = await self.readline()

        if val == b'':
            raise StopAsyncIteration

        return val


    @error_if_connection_closed
    async def read(self, n=None):
        """
        Read up to `n` bytes.

        If `n` is not provided, or negative, read until EOF and return all bytes.

        This method is a coroutine.
        """
        # default of None is more Pythonic than -1
        n = -1 if n is None or n < 0 else n
        data = await self.reader.read(n)
        return data


    @error_if_connection_closed
    async def readline(self):
        """
        Read one line, where "line" is a sequence of bytes ending with "\n".

        If EOF is received, and "\n" was not found, the method will return the partial read
        bytes.

        If the EOF was received and the internal buffer is empty, return an empty bytes
        object.

        This method is a coroutine.
        """
        line = await self.reader.readline()
        return line


    @error_if_connection_closed
    async def readexactly(self, n):
        """
        Read exactly `n` bytes.

        Raise an `asyncio.IncompleteReadError` if the end of the stream is reached before
        `n` can be read, the `asyncio.IncompleteReadError.partial` attribute of the
        exception contains the partial read bytes.

        This method is a coroutine.
        """
        data = await self.reader.readexactly(n)
        return data


    @error_if_connection_closed
    async def readuntil(self, separator=b'\n'):
        """
        Read data from the stream until `separator` is found.

        Raise an `asyncio.IncompleteReadError` if the end of the stream is reached before
        the complete separator is found, the `asyncio.IncompleteReadError.partial` attribute
        of the exception contains the partial read bytes.

        This method is a coroutine.
        """
        data = await self.reader.readuntil(separator)
        return data


    @error_if_connection_closed
    async def write(self, data):
        """
        Write some data bytes to the transport and flush the buffer.

        This method is a coroutine.
        """
        writer = self.writer
        writer.write(data)
        await writer.drain()


    @error_if_connection_closed
    async def writelines(self, data):
        """
        Write an iterable of data bytes to the transport and flush the buffer.

        This method is a coroutine.
        """
        writer = self.writer
        writer.writelines(data)
        await writer.drain()


    def __repr__(self):
        parts = (
            f'{nameof(type(self))}(',
            f'host={self.host!r}, '
            f'port={self.port!r}, '
            f'loop={self.loop!r}, '
            f'**{self.options!r})'
        )
        return ''.join(parts)
