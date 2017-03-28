import subprocess
import unittest
from test.test_support import EnvironmentVarGuard
from outlyer.plugin_helper import container

CONTAINER_ID = 'container_12345'
CONTAINER_IP = '123.45.667.890'


class TestDockerHelpers(unittest.TestCase):

    def setUp(self):
        self.env = EnvironmentVarGuard()

    def test_is_container_when_container_id(self):
        self.env.set('CONTAINER_ID', CONTAINER_ID)
        self.assertTrue(container.is_container())

    def test_not_container_when_no_container_id(self):
        self.env.unset('CONTAINER_ID')
        self.assertFalse(container.is_container())

    def test_conatiner_id(self):
        self.env.set('CONTAINER_ID', CONTAINER_ID)
        self.assertEqual(CONTAINER_ID, container.get_container_id())

    def test_conatiner_ip(self):
        self.env.set('CONTAINER_IP', CONTAINER_IP)
        self.assertEqual(CONTAINER_IP, container.get_container_ip())

    def test_patch_container(self):
        container.patch()
        self.assertTrue(hasattr(subprocess, '_check_output'))

    def test_unpatch_container(self):
        container.unpatch()
        self.assertFalse(hasattr(subprocess, '_check_output'))