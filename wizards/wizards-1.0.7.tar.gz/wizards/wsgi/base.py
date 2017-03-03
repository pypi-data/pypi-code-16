import contextlib
import logging

from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import InternalServerError
from werkzeug.exceptions import NotImplemented
from werkzeug.exceptions import UnsupportedMediaType

from wizards.wsgi.middleware import Middleware
from wizards.wsgi.request import Request


class BaseApplication:
    """A base class for WSGI applications.

    Args:
        methods: a list of methods that are allowed by this
            service. If no list is provided, it is assumed that
            all methods are allowed.
    """
    request_class = Request
    response_class = None

    def __init__(self, urls, handlers=None, debug=False, logger=None, middleware=None, accept=None, content_types=None, methods=None):
        self.urls = urls
        self.debug = debug
        self.logger = logger or logging.getLogger('wsgi')
        self.middleware = middleware or Middleware()
        self.accept = accept
        self.content_types = content_types
        self.methods = methods
        self.handlers = handlers or {}

    def request_factory(self, environ):
        """Create a new :attr:`request_class` instance using the
        WSGI environment provided by the webserver.
        """
        return self.request_class(environ)

    def call(self, request):
        self.validate_request_method(request)
        self.validate_content_type(request)
        adapter = self.bind_adapter(request.environ)
        endpoint, params = adapter.match()

        response = self.middleware.process_request(request)
        if response is not None:
            return response

        f = self.get_handler(endpoint)
        return f(request, **params)

    def __call__(self, environ, start_response):
        request = self.request_factory(environ)
        try:
            response = self.call(request)
        except HTTPException as e:
            response = e
        except Exception as e:
            response = InternalServerError()
            if self.debug:
                raise

        if isinstance(response, HTTPException):
            response = self.on_exception(request, response)

        assert callable(response), "handler result must be callable, got %s" % repr(response)
        return response(environ, start_response)

    def on_exception(self, request, response):
        """Invokes when an error condition arises."""
        return response

    def bind_adapter(self, environ):
        """Bind the URL adapter to the WSGI environment."""
        return self.urls.bind_to_environ(environ)

    def get_handler(self, name):
        """Return the request handler specified by `name`."""
        try:
            return self.handlers[name]
        except LookupError:
            self.logger.critical("No request handler registered for %s", name)
            raise

    def validate_request_method(self, request):
        """Validate that the request method is supported by the
        server.
        """
        if self.methods is None:
            return

        if request.method not in self.methods:
            raise NotImplemented

    def validate_content_type(self, request):
        """Validate the content type of an incoming request."""
        if self.content_types is None\
        or request.method not in ('POST','PUT','PATCH','DELETE'):
            return

        if request.mimetype not in self.content_types:
            raise UnsupportedMediaType

    @contextlib.contextmanager
    def override_handler(self, name, new):
        old = self.handlers.pop(name, None)
        self.handlers[name] = new
        try:
            yield
        finally:
            if old is not None:
                self.handlers[name] = old
