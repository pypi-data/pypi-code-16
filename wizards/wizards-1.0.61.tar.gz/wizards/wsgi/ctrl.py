import functools
import logging

from ea.lib.datastructures import DTO
import ioc
import ea.schema

from wizards.codec import Codec
from wizards.wsgi.response import Response
from wizards.wsgi.exc import RequestRejected


TEST_HDRS = set(['X-Test','X-Test-No-Invoke',
    'X-Test-Subject','X-Test-Roles','X-Test-Audience',
    'X-Test-Disable-Validation'])


class CtrlType(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(CtrlType, cls).__new__
        if name == 'BaseCtrl':
            return super_new(cls, name, bases, attrs)

        fields = {'dto_class': DTO}
        for key in list(attrs.keys()):
            if not isinstance(attrs[key], ea.schema.fields.Field):
                continue

            fields[key] = attrs.pop(key)

        attrs['schema_class'] = type('%sSchema' % name,
            (ea.schema.Schema,), fields)

        return super_new(cls, name, bases, attrs)


class BaseCtrl(metaclass=CtrlType):
    debug = ioc.class_property('settings.debug', default=False)
    response_class = ioc.class_property('WSGIResponse',
        default=Response)
    codec = ioc.class_property('WSGICodec', default=Codec())

    logger = logging.getLogger('wsgi')
    dto_class = DTO
    http_method_names = set(['get', 'post', 'put', 'patch', 'delete',
        'head', 'options', 'trace','connect'])
    content_types = [
        "application/json",
        "application/yaml"
    ]
    accepts = [
        "application/json",
        "application/yaml"
    ]
    schema_class = None

    @property
    def allowed_methods(self):
        return [m.upper() for m in
            sorted(self.http_method_names) if hasattr(self, m)]

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
            self.schema = self.get_schema(request)
            try:
                return self.dispatch(request, *args, **kwargs)
            except RequestRejected as e:
                return e.render_to_response(self.codec)

        view.view_class = cls
        view.view_initkwargs = initkwargs

        # take name and docstring from class
        functools.update_wrapper(view, cls, updated=())

        return view

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

    def dispatch(self, request, *args, **kwargs):
        """Dispatches the request to the appropriate request method
        handler.

        Validates that the controller can handle the incoming request. The
        controller checks if the client accepts the content types it can
        respond in. For PUT, POST and PATCH requests, also verify that
        the request payload can be decoded (if there is one).

        In the next stage, the payload is validated using the validation
        schema declared on the :class:`BaseCtrl` subclass.
        """
        if request.method.lower() not in self.http_method_names\
        or not hasattr(self, request.method.lower()):
            request.reject('HTTP_METHOD_NOT_ALLOWED',
                headers={'Allow': ', '.join(self.allowed_methods)})

        # Check on the existence any testing header.
        debug = self.debug
        hdrs = request.headers
        test_hdrs = set(hdrs.keys()) & TEST_HDRS
        if test_hdrs and debug:
            self.logger.critical("Be aware: debug mode is enabled and the "
                                 "following testing headers were sent by "
                                 "the client: %s" % ', '.join(sorted(test_hdrs)))

        must_invoke = True
        must_validate = True
        if debug:
            must_invoke ^= bool(hdrs.get('X-Test-No-Invoke'))
            must_validate ^= bool(hdrs.get('X-Test-Disable-Validation'))

        # Verify that the client accepts any of our content
        # types.
        accepts = request.accepts(self.content_types)
        if not accepts:
            request.reject('HTTP_NOT_ACCEPTED')

        # If there is a schema class defined, it is assumed that
        # the request MUST contain a body.
        if request.method in ('POST','PUT','PATCH') and must_validate:
            if not request.contains(self.content_types)\
            and self.schema is not None:
                request.reject('HTTP_UNSUPPORTED_MEDIA_TYPE')

            request.decode(self.codec, mandatory=self.schema is not None)
            assert hasattr(request, 'payload'),\
                "Request.payload must exist after Request.decode()"
            if self.schema is not None:
                assert request.payload is not None,\
                    "Request.payload can not be not at this point."
                request.payload, errors = self.schema.load(
                    self.pre_process_payload(request.payload))
                if errors:
                    request.reject('DTO_VALIDATION_ERROR', errors=errors)
                request.payload = self.dto_class(
                    self.post_process_payload(request.payload)).as_dto()


        # If the X-Test-No-Invoke header was used to suppress invocation,
        # bail out just before the pre-dispatch phase.
        if not must_invoke:
            return self.render_to_response(status=200)

        handler = getattr(self, request.method.lower())
        response = self.pre_dispatch(request)
        if response is not None:
            return response

        response = handler(request, *args, **kwargs)
        self.post_dispatch(request, response)

        return response

    def pre_dispatch(self, request, *args, **kwargs):
        """Hook to execute just before dispatching a request to its
        handler.
        """
        return None

    def post_dispatch(self, request, response, **kwargs):
        """Hook to execute just after dispatching a request to its
        handler.
        """
        return None

    def pre_process_payload(self, payload):
        """Preprocesses the request payload before invoking the
        validator.
        """
        return payload

    def post_process_payload(self, payload):
        """Postprocesses the request payload after being validated.
        At this point it can safely be assumed that the request
        payload has the desired format and structure.
        """
        return payload

    def serialize_response(self, request, payload):
        """Serialize `payload` just before returning a response to the
        client. Return the content type the payload was serialized to,
        and the serialized payload.
        """
        # At this point we can safely assume that the client will accept
        # any content type we serialize to.
        accepts = request.accepts(self.content_types)
        assert accepts, "Request should accept the content types we specified."
        return accepts, self.codec.encode(accepts, payload)


    def render_to_response(self, *args, **kwargs):
        return self.response_class(*args, **kwargs)

    def get_schema(self, request):
        """Return an instance of the schema class used to validate the
        request payload.
        """
        if self.schema_class is None:
            return

        return self.schema_class(many=False,
            partial=request.method=='PATCH')


class NotImplementedCtrl(BaseCtrl):

    def dispatch(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must override this method.")
