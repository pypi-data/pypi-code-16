import asyncio
import warnings
from functools import wraps
from logging import getLogger
from pika import ConnectionParameters
from pika.credentials import PlainCredentials
from pika.spec import REPLY_SUCCESS
from yarl import URL
from .channel import Channel
from .common import FutureStore
from .tools import copy_future
from .adapter import AsyncioConnection


log = getLogger(__name__)


def _ensure_connection(func):
    @wraps(func)
    @asyncio.coroutine
    def wrap(self, *args, **kwargs):
        if self.is_closed:
            raise RuntimeError("Connection closed")

        return (yield from func(self, *args, **kwargs))
    return wrap


class Connection:
    __slots__ = (
        'loop', '__closing', '_connection', '_futures', '__sender_lock',
        '_io_loop', '__connecting', '__connection_parameters', '__credentials',
        '__connection_lock',
    )

    def __init__(self, host: str = 'localhost', port: int = 5672, login: str = 'guest',
                 password: str = 'guest', virtual_host: str = '/',
                 ssl: bool = False, *, loop=None, **kwargs):

        self.loop = loop if loop else asyncio.get_event_loop()
        self._futures = FutureStore(loop=self.loop)

        self.__credentials = PlainCredentials(login, password) if login else None

        self.__connection_parameters = ConnectionParameters(
            host=host,
            port=port,
            credentials=self.__credentials,
            virtual_host=virtual_host,
            ssl=ssl,
            **kwargs
        )

        self._connection = None
        self.__connection_lock = asyncio.Lock(loop=self.loop)
        self.__connecting = self._futures.create_future()
        self.__closing = self._futures.create_future()

    def __str__(self):
        return 'amqp://{credentials}{host}:{port}/{vhost}'.format(
            credentials="{0.username}:********@".format(self.__credentials) if self.__credentials else '',
            host=self.__connection_parameters.host,
            port=self.__connection_parameters.port,
            vhost=self.__connection_parameters.virtual_host,
        )

    def __repr__(self):
        cls_name = self.__class__.__name__
        return '<{0}: "{1}">'.format(cls_name, str(self))

    def add_close_callback(self, callback):
        self.__closing.add_done_callback(callback)

    @property
    def is_closed(self):
        if not (self._connection and self._connection.socket):
            return True

        if self.closing.done():
            return True

        return False

    @property
    def closing(self):
        return copy_future(self.__closing)

    @asyncio.coroutine
    def connect(self):
        if self.closing.done():
            raise RuntimeError("Invalid connection state")

        with (yield from self.__connection_lock):
            self._connection = None

            log.debug("Creating a new AMQP connection: %s", self)

            f = self._futures.create_future()

            def _on_connection_refused(connection, message: str):
                _on_connection_lost(connection, code=500, reason=ConnectionRefusedError(message))

            def _on_connection_lost(_, code, reason):
                nonlocal f

                if self.__closing.done():
                    return

                if code == REPLY_SUCCESS:
                    return self.__closing.set_result(reason)

                if isinstance(reason, Exception):
                    exc = reason
                else:
                    exc = ConnectionError(reason, code)

                self.__closing.set_exception(exc)
                self._futures.reject_all(exc)

                if f.done():
                    return

                f.set_exception(exc)

            connection = AsyncioConnection(
                parameters=self.__connection_parameters,
                loop=self.loop,
                on_open_callback=f.set_result,
                on_close_callback=_on_connection_lost,
                on_open_error_callback=_on_connection_refused,
            )

            yield from f

            log.debug("Connection ready: %r", self)

            self._connection = connection

    @_ensure_connection
    @asyncio.coroutine
    def channel(self) -> Channel:

        log.debug("Creating AMQP channel for conneciton: %r", self)

        channel = Channel(self, self.loop, self._futures)

        yield from channel.initialize()

        log.debug("Channel created: %r", channel)
        return channel

    @asyncio.coroutine
    def close(self) -> None:
        log.debug("Closing AMQP connection")
        self._connection.close()
        yield from self.closing


@asyncio.coroutine
def connect(url: str=None, *, host: str='localhost',
                  port: int=5672, login: str='guest',
                  password: str='guest', virtualhost: str='/',
                  ssl: bool=False, loop=None, **kwargs) -> Connection:
    if url:
        url = URL(str(url))
        host = url.host or host
        port = url.port or port
        login = url.user or login
        password = url.password or password
        virtualhost = url.path[1:] if url.path else virtualhost

    connection = Connection(
        host=host, port=port, login=login, password=password,
        virtual_host=virtualhost, ssl=ssl, loop=loop, **kwargs
    )

    yield from connection.connect()
    return connection


@asyncio.coroutine
def connect_url(url: str, loop=None) -> Connection:
    warnings.warn(
        'Please use reconnect(url) instead connect_url(url)', DeprecationWarning
    )

    return (yield from connect(url, loop=loop))


__all__ = ('connect', 'connect_url', 'Connection')


