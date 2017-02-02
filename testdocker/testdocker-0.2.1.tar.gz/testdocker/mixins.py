"""
testdocker.mixins
~~~~~~~~~~~~~~

Unit Test mixins for testing docker containers.

:copyright: (c) 2016 by Joe Black.
:license: Apache2.
"""

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
        print('waiting for: %s' % cls.container)
        cls.container.wait()
        super(DockerTestMixin, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(DockerTestMixin, cls).tearDownClass()
        if cls.tear_down:
            cls.compose.down()


class ContainerTestMixin(DockerTestMixin):
    test_patterns = []
    test_tcp_ports = []
    test_udp_ports = []
    test_http_uris = []
    tear_down = True

    def test_container_is_healthy(self):
        self.assertEqual(self.container.health, 'healthy')

    def test_patterns_in_logs(self):
        for pattern in self.test_patterns:
            with self.subTest(pattern=pattern):
                self.assertRegex(self.container.logs, pattern)

    def test_tcp_ports_open(self):
        for port in self.test_tcp_ports:
            with self.subTest(port=port):
                cmd = commands.NetCatCommand('localhost', port)
                exit_code = self.container.exec(cmd, exit_code_only=True)
                self.assertEqual(exit_code, 0)

    def test_udp_ports_open(self):
        for port in self.test_udp_ports:
            with self.subTest(port=port):
                cmd = commands.NetCatCommand('localhost', port, udp=True)
                exit_code = self.container.exec(cmd, exit_code_only=True)
                self.assertEqual(exit_code, 0)

    def test_http_uris_reachable(self):
        for uri in self.test_http_uris:
            with self.subTest(uri=uri):
                cmd = commands.CurlCommand(uri)
                exit_code = self.container.exec(cmd, exit_code_only=True)
                self.assertEqual(exit_code, 0)
