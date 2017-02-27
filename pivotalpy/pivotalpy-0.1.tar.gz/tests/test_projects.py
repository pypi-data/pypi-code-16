import unittest
import json
import httpretty
from pivotalpy.client import PivotalClient

PROJECT_ID = '5'
TOKEN = 'Token'
BASE_PROJECT_URL = 'https://www.pivotaltracker.com/services/v5/projects/' + PROJECT_ID + '/'

class TestProject(unittest.TestCase):
    def setUp(self):
        self.driver = PivotalClient(TOKEN)

    def test_init(self):
        self.assertEquals(self.driver.auth.token, 'Token')

    # Test that exceptions are thrown when we get a bad response from Pivotal
    @httpretty.activate
    def test_api_fail(self):
        httpretty.register_uri(httpretty.GET, BASE_PROJECT_URL, body='Fail', status=400)
        httpretty.register_uri(httpretty.GET, BASE_PROJECT_URL + 'memberships/', body='Fail', status=400)

        with self.assertRaises(IOError):
            r = self.driver.project.get(PROJECT_ID)
            self.assertEquals(r.status_code, 400)

        with self.assertRaises(IOError):
            r = self.driver.project.get_memberships(PROJECT_ID)
            self.assertEquals(r.status_code, 400)

    # Test that getting projects work
    @httpretty.activate
    def test_get_project(self):
        body = json.dumps({ 'name' : 'A Project', 'kind' : 'project' })
        httpretty.register_uri(httpretty.GET, BASE_PROJECT_URL, body=body, status=200)

        r = self.driver.project.get(PROJECT_ID)

        self.assertEquals(r['name'], 'A Project')
        self.assertEquals(r['kind'], 'project')

    # Test that getting project memberships work
    @httpretty.activate
    def test_get_memberships(self):
        body = json.dumps([
            { 'name' : 'Bob' },
            { 'name' : 'Sally' },
            { 'name' : 'Daniel' }
        ])
        httpretty.register_uri(httpretty.GET, BASE_PROJECT_URL + 'memberships/', body=body, status=200)

        r = self.driver.project.get_memberships(PROJECT_ID)

        self.assertEquals(r[0]['name'], 'Bob')
        self.assertEquals(r[1]['name'], 'Sally')
        self.assertEquals(r[2]['name'], 'Daniel')
