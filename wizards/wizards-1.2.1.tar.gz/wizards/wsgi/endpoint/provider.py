import logging

from werkzeug.routing import Map
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import MethodNotAllowed

from wizards.wsgi.handler import RequestHandler
from wizards.wsgi.endpoint.base import Endpoint


class EndpointProvider:
    """Provides endpoints for the main event loop of a WSGI
    application.
    """
    logger = logging.getLogger("wsgi")

    @classmethod
    def fromlist(cls, endpoints):
        return cls([Endpoint(**x) for x in endpoints])

    def __init__(self, endpoints):
        self.urls = Map([x.rule for x in endpoints])
        self.endpoints = {x.name: x for x in endpoints}

    def get(self, request):
        """Return the :class:`Endpoint` for the :class:`Request`
        or raise :exc:`werkzeug.exceptions.NotFound.
        """
        adapter = self.urls.bind_to_environ(request.environ)
        try:
            name, params = adapter.match()
        except MethodNotAllowed:
            request.reject('HTTP_METHOD_NOT_ALLOWED')
        except NotFound:
            request.reject('RESOURCE_DOES_NOT_EXIST')
        return RequestHandler(request, self.get_endpoint(name), params)

    def get_endpoint(self, name):
        """Return the endpoint identified by `name`."""
        return self.endpoints[name]

    def reverse(self, name, **kwargs):
        """Reverse an endpoint name to an URL."""
        return self.urls.bind('').build(name, kwargs)


class NullEndpointProvider(EndpointProvider):

    def __init__(self, *args, **kwargs):
        EndpointProvider.__init__(self, [])
