# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""Testing tools."""

from aiohttp import request
import asyncio
import socket


def get_unused_port():
    """Return a unused port on localhost."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TestClient:
    """Hypr application test client.

    The test client allow a user to perform HTTP requests to a Hypr application
    by providing the full client interface of aiohttp. It works as a context
    manager to automatically clean-up everything whean leaving it.
    """

    def __init__(self, app):
        """Init a test client.

        Args:
            app: a Hypr application.
        """
        self.app = app
        self.srv = None
        self.port = None
        self.handler = self.app.make_handler()

    @asyncio.coroutine
    def create_server(self):
        """Create a server."""
        self.port = get_unused_port()
        self.srv = yield from self.app.loop.create_server(
            self.handler, '127.0.0.1', self.port)

    def __enter__(self):
        """Entering the context manager."""
        if self.srv is None:
            self.app.loop.run_until_complete(self.create_server())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Leaving the context manager."""
        if self.srv is not None:
            self.srv.close()
            self.app.loop.run_until_complete(self.handler.finish_connections())
            self.srv = None

    def request(self, method, path, **kwargs):
        """Perform an HTTP request.

        Args:
            method (str): HTTP method.
            url (str): Requested URL.
            kwargs: see ``aiohttp.request`` available parameters.

        Returns:
            Return a ``client response`` object.
        """
        kwargs['loop'] = self.app.loop

        @asyncio.coroutine
        def do_request():

            if self.srv is None:
                yield from self.create_server()  # pragma: no cover

            assert path.startswith('/'), '`path` should start with a \'/\'.'

            kwargs['url'] = 'http://127.0.0.1:{}'.format(self.port) + path
            rv = yield from request(method, **kwargs)
            rv.text = yield from rv.text()
            return rv

        return self.app.loop.run_until_complete(do_request())

    def get(self, path, **kwargs):
        """Perform a HTTP GET request."""
        return self.request('GET', path, **kwargs)

    def head(self, path, **kwargs):
        """Perform a HTTP HEAD request."""
        return self.request('HEAD', path, **kwargs)

    def options(self, path, **kwargs):
        """Perform a HTTP OPTIONS request."""
        return self.request('OPTIONS', path, **kwargs)

    def post(self, path, **kwargs):
        """Perform a HTTP POST request."""
        return self.request('POST', path, **kwargs)

    def put(self, path, **kwargs):
        """Perform a HTTP PUT request."""
        return self.request('PUT', path, **kwargs)

    def patch(self, path, **kwargs):
        """Perform a HTTP PACTH request."""
        return self.request('PATCH', path, **kwargs)

    def delete(self, path, **kwargs):
        """Perform a HTTP DELETE request."""
        return self.request('DELETE', path, **kwargs)
