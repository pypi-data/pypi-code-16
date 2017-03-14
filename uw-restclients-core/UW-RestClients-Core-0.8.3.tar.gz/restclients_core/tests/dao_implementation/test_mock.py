from unittest import TestCase
from restclients_core.dao import DAO
from os.path import abspath, dirname
from restclients_core.dao import MockDAO


class TDAO(DAO):
    def service_name(self):
        return 'testing'

    def service_mock_paths(self):
        return [abspath(dirname(__file__) + "/resources/")]


class TestMock(TestCase):
    def test_found_resource(self):
        response = TDAO().getURL('/found.json', {})
        self.assertEquals(response.status, 200)
        self.assertEquals(response.read(), '{"OK": true }\n')

    def test_missing_resource(self):
        response = TDAO().getURL('/missing.json', {})
        self.assertEquals(response.status, 404)

    def test_file_headers(self):
        response = TDAO().getURL('/with_headers.json', {})
        self.assertEquals(response.status, 202)

        self.assertEquals(response.headers["Custom"], "My Custom Value")
        self.assertEquals(response.getheader("Custom"), "My Custom Value")

    def test_plain_file_headers(self):
        response = TDAO().getURL('/with_only_headers.json', {})
        self.assertEquals(response.status, 200)

        self.assertEquals(response.headers["Custom2"], "My Custom Value 2")

    def test_registered_paths(self):
        response = TDAO().getURL('/override.json', {})
        self.assertEquals(response.status, 200)
        self.assertEquals(response.read(), '{"override": false }\n')

        override = abspath(dirname(__file__) + "/resource_override/")
        MockDAO.register_mock_path(override)

        response = TDAO().getURL('/override.json', {})
        self.assertEquals(response.status, 200)
        self.assertEquals(response.read(), '{"override": true }\n')

    def test_binary_data(self):
        response = TDAO().getURL('/image.jpg', {})
        self.assertEquals(response.status, 200)
