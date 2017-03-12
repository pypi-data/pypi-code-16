import logging

import ioc

from werkzeug.exceptions import HTTPException
from wizards.codec import Codec
from wizards.wsgi.exc import RequestRejected
from wizards.wsgi.request import Request
from wizards.wsgi.response import Response
from wizards.wsgi.endpoint import NullEndpointProvider


class WSGIApplication:
    logger = logging.getLogger('wsgi')
    request_class = ioc.class_property('WSGIRequest',
        default=Request)
    response_class = ioc.class_property('WSGIResponse',
        default=Response)
    provider = ioc.class_property('WSGIEndpointProvider',
        default=NullEndpointProvider())
    debug = ioc.class_property('settings.debug', default=False)
    codec = ioc.class_property('WSGICodec', default=Codec())
    content_types = [
        "application/json",
        "application/yaml"
    ]

    def on_request(self, request):
        pass

    def on_response(self, request, response):
        pass

    def __call__(self, environ, start_response):
        request = self.request_class(environ)
        self.on_request(request)
        try:
            handler = self.provider.get(request)
            response = handler.handle(request)
        except HTTPException as e:
            if self.debug:
                raise
            response = e
        except RequestRejected as e:
            response = e.render_to_response(self.codec)

        except Exception as e:
            # This is a very fatal condition meaning that there
            # was an exception and at no point in the request
            # handling it got caught.
            self.logger.exception("Catastrophic programming fail.")
            raise

        self.on_response(request, response)
        return response(environ, start_response)
