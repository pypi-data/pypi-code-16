"""
chitchat.client
~~~~~~~~~~~~~~~

This module contains
"""
import asyncio
from asyncio import gather, get_event_loop, CancelledError, Task
from contextlib import suppress

from .connection import Connection
from .messaging.incoming import parse as parse_message
from .utils import aiterdecode


class Client:


    def __init__(self, host, port, *, connection_factory=Connection, encoding='UTF-8', **kwargs):
        self.connection = connection_factory(host, port, **kwargs)
        self.encoding = encoding


    def shutdown(self, loop):
        """Cancel running tasks and stop the event loop."""
        task = gather(*Task.all_tasks(loop=loop), loop=loop, return_exceptions=True)
        task.cancel()
        with suppress(CancelledError):
            # loop stops as soon as task is cancelled
            loop.run_forever()


    def run_blocking(self, *, loop=None):
        """Connect to the server, blocking until the connection is closed."""
        loop = loop or get_event_loop()
        task = loop.create_task(self.run())

        try:
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            self.shutdown(loop)


    async def run(self):
        """
        Connect to the server, passing each line received to `self.handle`.

        This method is a coroutine.
        """
        conn = self.connection

        async with conn:
            async for line in aiterdecode(conn, self.encoding):
                # conn.loop.create_task(self.handle(line))
                await self.handle(line)


    async def handle(self, line):
        """
        Parse a server response and arrange for the relevant callbacks to be triggered.

        This method is a coroutine.
        """
        message = parse_message(line)
        await self.trigger(**message)


    async def trigger(self, command, *args, **kwargs):
        """
        Schedule callbacks to be run.
        """
        loop = self.connection.loop
        callbacks = self.callbacks[command] | self.callbacks[ALL]

        for cb in callbacks:
            loop.create_task(cb())
