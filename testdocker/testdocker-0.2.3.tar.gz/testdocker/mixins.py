"""
testdocker.mixins
~~~~~~~~~~~~~~

Unit Test mixins for testing docker containers.

:copyright: (c) 2016 by Joe Black.
:license: Apache2.
"""

import unittest

from colour_runner.runner import ColourTextTestRunner
from colour_runner.result import ColourTextTestResult

from . import objects, commands


class ConfigurationError(Exception):
    """"""


class DockerTestMixin:
    compose = objects.Compose

    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, 'name'):
            raise ConfigurationError('Test class missing name attribute')
        cls.compose.up()
        cls.container = objects.Container(cls.name)
        print('Waiting for: %s container to be ready...' % cls.container.name)
        cls.container.wait()
        super(DockerTestMixin, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(DockerTestMixin, cls).tearDownClass()
        if cls.tear_down:
            cls.compose.down()

    def defaultTestResult(self):
        return ColourTextTestResult(
            descriptions=True,
            verbosity=2
        )


class ContainerTestMixin(DockerTestMixin):
    """For testing <project> container.

    Attributes:
        name:
            (str) Name for container.
        tear_down:
            (bool) Should ``docker-compose down`` be run in ``tearDownClass?``.
        test_patterns:
            (list) Regex patterns to assert in  container logs.
        test_tcp_ports:
            (list) TCP Ports to assert are open
        test_upd_ports:
            (list) TCP Ports to assert are open
        test_http_uris:
            (list) HTTP URI's to test are reachable
    """

    name = ''
    tear_down = True
    test_patterns = []
    test_tcp_ports = []
    test_udp_ports = []
    test_http_uris = []

    def test_container_is_healthy(self):
        """Assert container healthcheck is passing"""
        self.assertEqual(self.container.health, 'healthy')

    def test_patterns_in_logs(self):
        """Assert test_patterns appear in container logs"""
        logs = self.container.logs
        for pattern in self.test_patterns:
            with self.subTest(pattern=pattern):
                self.assertRegex(logs, pattern)

    def test_tcp_ports_open(self):
        """Assert test_tcp_ports are open"""
        for port in self.test_tcp_ports:
            with self.subTest(port=port):
                cmd = commands.NetCatCommand('localhost', port)
                exit_code = self.container.exec(cmd, exit_code_only=True)
                self.assertEqual(exit_code, 0)

    def test_udp_ports_open(self):
        """Assert test_udp_ports are open"""
        for port in self.test_udp_ports:
            with self.subTest(port=port):
                cmd = commands.NetCatCommand('localhost', port, udp=True)
                exit_code = self.container.exec(cmd, exit_code_only=True)
                self.assertEqual(exit_code, 0)

    def test_http_uris_reachable(self):
        """Assert test_http_uris are reachable"""
        for uri in self.test_http_uris:
            with self.subTest(uri=uri):
                cmd = commands.CurlCommand(uri)
                exit_code = self.container.exec(cmd, exit_code_only=True)
                self.assertEqual(exit_code, 0)


def main():
    unittest.main(
        testRunner=ColourTextTestRunner(verbosity=2, descriptions=True),
        verbosity=2,
    )
