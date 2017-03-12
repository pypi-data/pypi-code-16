import ioc

class RequestHandler:
    """Handles an incoming request and returns a :class:`Response`
    instance.
    """
    authenticator = ioc.class_property('WSGIRequestAuthenticator')

    def __init__(self, request, endpoint, params):
        self.request = request
        self.endpoint = endpoint
        self.params = params

    @property
    def content_types(self):
        return set(self.endpoint.content_types)\
            & set(self.serializer.content_types)

    def handle(self, request):
        self.authenticator.authenticate(request)
        self.endpoint.authorize(request)
        return self.endpoint.handle(request)
