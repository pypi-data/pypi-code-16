import copy

import ioc

from wizards.codec import Codec
from wizards.wsgi.authenticator import HeadersRequestAuthenticator
from wizards.wsgi.endpoint import EndpointProvider
from wizards.wsgi.endpoint import Endpoint
from wizards.wsgi.exc import RequestRejected
from wizards.testing.ctrl import ControllerTestCase


class EndpointTestCase(ControllerTestCase):
    endpoint_name = None
    authenticator_class = HeadersRequestAuthenticator
    provider_class = EndpointProvider
    default_url_params = None
    url_params = None
    subject = 0
    roles = []
    audience = []
    methods = []
    codec = Codec()

    @property
    def url(self):
        assert self.endpoint_name is not None,\
            "%s must specify the `endpoint_name` attribute." % type(self).__name__
        return self.reverse()

    def setUp(self):
        super(EndpointTestCase, self).setUp()
        self.provider = self.provider_class([
            Endpoint(self.endpoint_name, self.path,
                authenticate=self.auth, roles=self.roles,
                aud=self.audience, methods=self.methods)
        ])

        if not self.url_params:
            self.url_params = copy.deepcopy(self.default_url_params)

        self.authenticator = self.authenticator_class(
            subject='X-Test-Subject',
            roles='X-Test-Roles',
            audience='X-Test-Audience')

        ioc.provide("%s:ctrl" % self.endpoint_name, self.ctrl)
        ioc.provide('WSGIRequestAuthenticator', self.authenticator)

    def tearDown(self):
        ioc.teardown()

    def handle(self, request):
        try:
            return self.provider.get(request).handle(request)
        except RequestRejected as e:
            return e.render_to_response(self.codec)

    def request(self, *args, **kwargs):
        headers = kwargs.pop('headers', {})
        if kwargs.pop('subject', True) and self.authenticator.subject not in headers:
            headers[self.authenticator.subject] = self.subject

        if kwargs.pop('roles', True) and self.roles\
        and self.authenticator.roles not in headers:
            headers[self.authenticator.roles] = ', '.join(self.roles)

        if kwargs.pop('aud', True) and self.audience\
        and self.authenticator.audience not in headers:
            headers[self.authenticator.audience] = self.audience[0]

        kwargs['headers'] = headers
        return super(EndpointTestCase, self).request(*args, **kwargs)

    def reverse(self, **kwargs):
        if self.url_params and not kwargs:
            kwargs.update(self.url_params)
        return self.provider.reverse(self.endpoint_name, **kwargs)
