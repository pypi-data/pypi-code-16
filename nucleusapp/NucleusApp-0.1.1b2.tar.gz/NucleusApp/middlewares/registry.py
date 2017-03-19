import logging

from ..app.imports import import_attr
from ..chest import Chest
from . import BaseMiddleware

log = logging.getLogger('NucleusApp')


class MiddlewareRegistry:
    def __init__(self, application, middlewares=()):
        self.application = application

        self.middlewares = {}

        self.ready = False

        if middlewares is not None:
            self.populate(middlewares)

    def populate(self, middlewares=None):
        if self.ready:
            return
        for middleware_name in middlewares:
            log.debug('Loader: Load middleware "{}"'.format(middleware_name))
            module_name, _, class_name = middleware_name.rpartition('.')
            if not module_name:
                raise RuntimeError(f"Middleware class '{middleware_name}' is not found!")
            middleware_class = import_attr(module_name, class_name)
            if not issubclass(middleware_class, BaseMiddleware) or middleware_class is BaseMiddleware:
                raise TypeError(f"Middleware must be subclass of BaseMiddleware")
            middleware = middleware_class()
            self.middlewares[middleware_name] = middleware
            Chest().root['middleware:' + middleware_name] = middleware
            Chest().root.lock_filed('middleware:' + middleware_name)

        self.ready = True

    def call(self, method, middleware=None, args=None, kwargs=None):
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = []

        if middleware is None:
            for obj in self.middlewares.keys():
                self.call(method, obj, args, kwargs)
        elif isinstance(middleware, (list, tuple, set)):
            for obj in middleware:
                self.call(method, obj, args, kwargs)
        else:
            middleware = self.middlewares[middleware]
            method = getattr(middleware, method)
            return method(*args, **kwargs)

    def populate_module(self, appconfig):
        self.call('populate_module', args=[appconfig])

    def start_application(self):
        self.call('start_application')
