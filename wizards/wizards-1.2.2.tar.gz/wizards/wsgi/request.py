import werkzeug.wrappers
import ioc

from wizards.wsgi.exc import RequestRejected
from wizards.wsgi.response import Response

NO_SUBJECT_ID = object()


class Request(werkzeug.wrappers.Request):
    response_class = ioc.class_property('WSGIResponse',
        default=Response)

    def __init__(self, *args, **kwargs):
        self.subject = None
        self.payload = None
        super(Request, self).__init__(*args, **kwargs)

    def accepts(self, content_types):
        """Return the most appropriate content type the client
        wishes to receive, based on the ``Accept`` header.
        """
        return self.accept_mimetypes.best_match(content_types)

    def contains(self, content_types):
        """Return a boolean indicating if any of the content types is
        contained in the request body.
        """
        if self.headers.get('Content-Type') is None:
            self.reject('HTTP_MISSING_CONTENT_TYPE')

        return self.headers.get('Content-Type') in set(content_types)

    def reject(self, code, headers=None, *args, **kwargs):
        """Reject the request with the error state defined by `code`."""
        raise RequestRejected(code, request=self, *args, **kwargs)

    def decode(self, codec, mandatory=False):
        """Decode the request body using `codec`. If the body could not be
        decoded, reject the request. Upon succesful decoding, set the
        :class:`Request.payload` attribute.

        Args:
            mandatory (bool): indicates if a request body is mandatory.
        """
        body = self.get_data() or getattr(self, 'payload', b'')
        if not body and mandatory:
            self.reject('HTTP_REQUEST_BODY_REQUIRED',
                message="%s %s requires that the request entity "
                        "has a body." % (self.method, self.path))

        try:
            mimetype = self.headers['Content-Type']
            body = codec.decode(mimetype, body)
        except codec.Undecodable:
            self.reject('HTTP_UNSUPPORTED_MEDIA_TYPE',
                message="Could not interpret the request payload as "
                        "%s." % mimetype)

        self.payload = body

    def respond(self, *args, **kwargs):
        """Responde to the request."""
        return self.response_class(*args, **kwargs)

    def is_authenticated(self):
        if self.subject is None:
            return False

        return self.subject.is_authenticated()
