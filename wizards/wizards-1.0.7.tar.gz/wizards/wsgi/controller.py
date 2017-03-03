import functools
import logging

from werkzeug.exceptions import MethodNotAllowed


class Controller(object):
    """
    Intentionally simple parent class for all controllers. Only implements
    dispatch-by-method and simple sanity checking.
    """
    http_method_names = ['get', 'post', 'put', 'patch', 'delete',
        'head', 'options', 'trace']
    response_class = None
    serializers = None

    def __init__(self, **kwargs):
        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.logger = logging.getLogger('wsgi.request')

    @classmethod
    def as_view(cls, **initkwargs):
        """
        Main entry point for a request-response process.
        """
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError("You tried to pass in the %s method name as a "
                                "keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r. as_view "
                                "only accepts arguments that are already "
                                "attributes of the class." % (cls.__name__, key))

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            self.request = request
            self.args = args
            self.kwargs = kwargs
            return self.dispatch(request, *args, **kwargs)

        view.view_class = cls
        view.view_initkwargs = initkwargs

        # take name and docstring from class
        functools.update_wrapper(view, cls, updated=())

        return view

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed

        response = self.pre_dispatch(request, handler, *args, **kwargs)
        if response is not None:
            return response

        response = handler(request, *args, **kwargs)
        self.post_dispatch(request, response, *args, **kwargs)

        return response

    def pre_dispatch(self, request, handler, *args, **kwargs):
        """Hook to execute just before dispatching a request to its
        handler.
        """
        return None

    def post_dispatch(self, request, response, **kwargs):
        """Hook to execute just after dispatching a request to its
        handler.
        """
        return None

    def http_method_not_allowed(self, request, *args, **kwargs):
        self.logger.warning(
            'Method Not Allowed (%s): %s', request.method, request.path,
            extra={'status_code': 405, 'request': request}
        )
        raise MethodNotAllowed(valid_methods=self._allowed_methods())

    def options(self, request, *args, **kwargs):
        """
        Handles responding to requests for the OPTIONS HTTP verb.
        """
        headers = {
            'Allow': ', '.join(self._allowed_methods()),
            'Content-Length': '0'
        }
        response = self.response_factory(headers=headers)
        return response

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]

    def response_factory(self, response=None, status=None, headers=None):
        """Create a new :class:`Response`."""
        return self.response_class(
            response=response,
            status=status,
            headers=headers
        )

    def render_to_response(self, payload=None, status=None, headers=None, content_type=None, **kwargs):
        kwargs['headers'] = headers or {}
        if content_type is not None:
            kwargs['headers'].setdefault('Content-Type', content_type)
        return self.response_class(response=payload, status=status, **kwargs)
