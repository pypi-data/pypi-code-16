import unittest
from test.test_support import EnvironmentVarGuard
from outlyer.plugin_helper.container import crequests

CONTAINER_ID = 'container_12345'
CONTAINER_IP = '123.45.667.890'


class TestDockerHelpers(unittest.TestCase):

    def setUp(self):
        self.env = EnvironmentVarGuard()

    def test_sanitise_endpoint(self):
        self.env.set('CONTAINER_IP', CONTAINER_IP)
        self.env.set('CONTAINER_ID', CONTAINER_ID)
        se = crequests.sanitize_container_endpoint("http://localhost/blah")
        self.assertEqual('http://%s/blah' % CONTAINER_IP, se)

    def test_sanitise_endpoint_port(self):
        self.env.set('CONTAINER_IP', CONTAINER_IP)
        self.env.set('CONTAINER_ID', CONTAINER_ID)
        se = crequests.sanitize_container_endpoint("http://localhost:43/blah")
        self.assertEqual('http://%s:43/blah' % CONTAINER_IP, se)

    def test_sanitise_endpoint_not_docker(self):
        self.env.unset('CONTAINER_ID')
        self.env.set('CONTAINER_IP', CONTAINER_IP)
        ep = "http://localhost:43/blah"
        se = crequests.sanitize_container_endpoint(ep)
        self.assertEqual(ep, se)

    def test_sanitise_endpoint_no_container_ip(self):
        self.env.unset('CONTAINER_IP')
        self.env.set('CONTAINER_ID', CONTAINER_ID)
        ep = "http://localhost:43/blah"
        se = crequests.sanitize_container_endpoint(ep)
        self.assertEqual(ep, se)