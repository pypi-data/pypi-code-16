import unittest

from werkzeug.test import EnvironBuilder
import ioc

from wizards.wsgi import Response
from wizards.wsgi import Request


class BaseWSGITestCase(unittest.TestCase):
    request_class = ioc.class_property('WSGIRequest',
        default=Request)
    response_class = ioc.class_property('WSGIRequest',
        default=Response)
    content_type = 'application/json'
    invoke = False
    disable_validation = False
    subject = '0'

    def get_headers(self):
        headers = {
            'X-Test': '1',
            'Accept': self.content_type
        }
        if not self.invoke:
            headers['X-Test-No-Invoke'] = '1'

        if self.disable_validation:
            headers['X-Test-Disable-Validation'] = '1'

        return headers

    def request(self, method, url, *args, **kwargs):
        kwargs['headers'] = kwargs.pop('headers', None) or {}
        kwargs['headers'].update(self.get_headers())
        if method in ('POST','PUT','PATCH'):
            kwargs['headers']['Content-Type'] = self.content_type
        env = EnvironBuilder(url, method=method, *args, **kwargs)
        return self.request_class(env.get_environ())

    def get(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.request('PATCH', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('POST', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request('PUT', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request('DELETE', *args, **kwargs)

    def options(self, *args, **kwargs):
        return self.request('OPTIONS', *args, **kwargs)

    def trace(self, *args, **kwargs):
        return self.request('TRACE', *args, **kwargs)

    def head(self, *args, **kwargs):
        return self.request('HEAD', *args, **kwargs)

    def connect(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def setUp(self):
        ioc.provide('settings.debug', True, force=True)

    def tearDown(self):
        ioc.teardown()

    def assertValidError(self, dto):
        pass # TODO
