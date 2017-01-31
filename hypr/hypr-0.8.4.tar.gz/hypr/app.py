# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""Application factory."""


import asyncio

from aiohttp.web import Application
from aiohttp.log import web_logger
from hypr.request import Request
from hypr.serializers import json_serializer
from hypr.config import Config
from hypr.globals import LocalStorage
from hypr.testing import TestClient
from hypr.router import Router


class Hypr(Application):
    """Hypr runs your application.

    The Hypr object provides a full asynchronous web server based on aiohttp
    and is the corner stone of your application. You will use it to register
    rules, associate them with providers and configure various features.
    """

    config_class = Config
    router_class = Router
    request_class = Request

    serializers = {
        'application/json': json_serializer
    }

    default_config = {
        'DEBUG': False,
        'DEFAULT_MIMETYPE': 'application/json',
        'CRUD_DEFAULT_LIMIT': 10,
        'CRUD_ABSOLUTE_LIMIT': 100,
        'MODELS_SQLITE_DATABASE_URI': 'file:/dev/null?mode=memory&cache=shared'
    }

    def __init__(self, *, logger=web_logger, loop=None,
                 router=None,
                 middlewares=(), debug=...):
        """Initialize the application."""
        if router is None:
            router = self.router_class(self)

        super().__init__(logger=logger, loop=loop, router=router,
                         middlewares=middlewares, debug=debug)

        LocalStorage.bind(self)     # initialize the context storage

        self.config = self.config_class(default=self.default_config)
        self.router.set_serializers(self.serializers)

    @property
    def available_mimetypes(self):
        """Return available mimetypes."""
        # TODO: improve performances by caching the result
        default_mimetype = self.config.get('DEFAULT_MIMETYPE')

        rv = [default_mimetype]
        rv.extend(self.serializers.keys())
        return rv

    def register_on_request_teardown(self, func, *args, **kwargs):
        """Register callbacks to execute on the request teardown."""
        callbacks = LocalStorage().get('_request_teardown_callbacks', None)
        if callbacks is None:
            callbacks = []
            LocalStorage().set('_request_teardown_callbacks', callbacks)
        callbacks.insert(0, (func, args, kwargs))

    def request_teardown(self):
        """Execute callbacks on the request teardown."""
        callbacks = LocalStorage().get('_request_teardown_callbacks', [])
        for (cb, args, kwargs) in callbacks:
            # TODO: handle exceptions
            res = cb(*args, **kwargs)
            if (asyncio.iscoroutine(res) or isinstance(res, asyncio.Future)):
                yield from res

    def add_provider(self, provider, *urls, methods=None, endpoint=None):
        """Register a provider.

        Args:
            provider: a Provider class.
            *urls: one or more path to access the provider.
            methods: a tuple containing the allowed HTTP methods.
                If methods is none, the allowed methods are determined from
                the provider implementation.
            endpoint: the name of the endpoint. If endpoint is none, the name
                is the provider's name.
        """
        self.router.add_provider(provider, *urls, methods=methods,
                                 endpoint=endpoint, propagation=True)

    def provide(self, *urls):
        """A decorator used to register a provider with URL rules.

        This does the same thing as add_provider() but is intended for
        decorator usage:

            @app.provide('/')
            class SomeProvider(Provider):
                ...

        See the documentation for add_provider() for more informations.
        """
        def decorator(provider):
            self.add_provider(provider, *urls)
            return provider
        return decorator

    def test_client(self):
        """Get a test client for this application.

        Being able to test your application is a mandatory requirement if you
        want to provide your users with trustful software. The test_client()
        aims to facilitate the testability of it by providing a full
        implementation of the aiohttp client API.

        The following example illustrates how to use it in a test:

            def test_get_response(self, app):

                with app.test_client() as client:
                    rv = client.get('/test')
                    assert rv.status == 200

        Where `app` is an instance of the application under test.
        """
        return TestClient(self)

    def _make_request(self, message, payload, protocol):
        return self.request_class(
            message, payload,
            protocol.transport, protocol.reader, protocol.writer,
            protocol.time_service, protocol._request_handler,
            secure_proxy_ssl_header=self._secure_proxy_ssl_header
        )

    def make_handler(self, *, secure_proxy_ssl_header=None, **kwargs):
        # Apply declarative propagations before the server startup.
        self.router._propagate()
        return super().make_handler(
            secure_proxy_ssl_header=secure_proxy_ssl_header, **kwargs)

    def run(self, host='127.0.0.1', port=5555, **options):  # pragma: no cover
        """
        Run the application as a web server.

        The application will run as a web server indefinitely until being
        interrupted with a Ctrl-C or a signal.

        Args:
            host: the hostname or IP adress of the application.
            port: the port to listen to.
        """
        loop = self.loop
        handler = self.make_handler(**options)

        task = loop.create_server(handler, host, port)
        server = loop.run_until_complete(task)

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            loop.run_until_complete(handler.finish_connections(1.0))
            server.close()
            loop.run_until_complete(server.wait_closed())
            loop.run_until_complete(self.finish())
        loop.close()
