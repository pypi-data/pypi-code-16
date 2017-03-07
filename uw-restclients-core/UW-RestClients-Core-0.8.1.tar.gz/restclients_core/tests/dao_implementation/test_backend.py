from unittest import TestCase
from restclients_core.dao import DAO, MockDAO
from restclients_core.models import MockHTTP
from restclients_core.exceptions import ImproperlyConfigured


class TDAO(DAO):
    def service_name(self):
        return "backend_test"

    def get_default_service_setting(self, key):
        if "DAO_CLASS" == key:
            return ('restclients_core.tests.dao_implementation.'
                    'test_backend.Backend')


class E1DAO(TDAO):
    def get_default_service_setting(self, key):
        if "DAO_CLASS" == key:
            return ('restclients_core.tests.dao_implementation.'
                    'test_backendX.Backend')


class E2DAO(TDAO):
    def get_default_service_setting(self, key):
        if "DAO_CLASS" == key:
            return ('restclients_core.tests.dao_implementation.'
                    'test_backend.BackendX')


class TestBackend(TestCase):
    def test_get(self):
        response = TDAO().getURL('/ok')
        self.assertEquals(response.data, 'ok - GET')

    def test_post(self):
        response = TDAO().postURL('/ok')
        self.assertEquals(response.data, 'ok - POST')

    def test_put(self):
        response = TDAO().putURL('/ok', {}, '')
        self.assertEquals(response.data, 'ok - PUT')

    def test_delete(self):
        response = TDAO().deleteURL('/ok')
        self.assertEquals(response.data, 'ok - DELETE')

    def test_patch(self):
        response = TDAO().patchURL('/ok', {}, '')
        self.assertEquals(response.data, 'ok - PATCH')

    def test_error_level1(self):
        self.assertRaises(ImproperlyConfigured, E1DAO().getURL, '/ok')

    def test_error_level2(self):
        self.assertRaises(ImproperlyConfigured, E2DAO().getURL, '/ok')


class Backend(MockDAO):
    def load(self,  method, url, headers, body):
        response = MockHTTP()
        response.status == 404
        response.data = "ok - %s" % method

        return response
