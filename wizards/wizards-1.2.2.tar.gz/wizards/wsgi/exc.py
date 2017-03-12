import logging
import uuid

import wizards.errors


class RequestRejected(Exception):
    """Raised when a WSGI request gets rejected - resulting
    in the server responding with a non-2xx status code.
    """
    logger = logging.getLogger('wsgi.rejected')
    content_types = [
        "application/json",
        "application/yaml"
    ]

    def __init__(self, code, request, **kwargs):
        self.code = code
        self.request = request
        self.properties = kwargs
        self.headers = kwargs.pop('headers', None)
        self.id = str(uuid.uuid4())

    def render_to_response(self, codec):
        # Get the content type based on the Accept header, and if
        # no suitable match could be found, use the default
        # content type.
        accept = self.request.accepts(self.content_types)
        if accept is None:
            accept = self.content_types[0]

        msg = self.dump()
        self.logger.info("Request rejected (id: %s, status: %s, code: %s) "
                         "message: %s"
                         % (self.id, msg['status'], self.code, msg['message']))

        payload = codec.encode(accept, msg)
        return self.request.respond(payload, status=msg['status'],
            headers=self.headers, content_type=accept)

    def dump(self):
        base = wizards.errors.get(self.code)
        base.update(self.properties)
        base.setdefault('detail', None)
        base.setdefault('hint', None)
        return dict(base)
