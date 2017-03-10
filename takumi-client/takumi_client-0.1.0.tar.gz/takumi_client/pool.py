# -*- coding: utf-8 -*-

"""
takumi_client.pool
~~~~~~~~~~~~~~~~~~


with clients['takumi_demo'].client_ctx() as c:
    c.ping_api()


CLIENT_SETTINGS = {
    'takumi_demo': {
        'service_name': 'PingService',
        'thrift_file': 'ping.thrift',
        'hosts_class': 'takumi_client.hosts.RedisHosts',
        'hosts': [
            ('localhost', 1990),
            ('localhost', 1991)
        ]
    }
}
"""

import os
import socket
import contextlib
import collections
import random
import time
import schema

from thriftpy import load
from thriftpy.transport import TBufferedTransport, TSocket, TTransportException
from thriftpy.protocol import TBinaryProtocol
from takumi_thrift.client import Client
from takumi_config import config
from takumi_config.utils import load_class


class Pool(object):
    """Client pool implementation

    Example::

        pool = Pool('test_client', PingService,
                    [('localhost', 1990), ('localhost', 1991)])
        with pool.client_ctx() as c:
            c.ping()

    :param client_name: the name of the client
    :param service: thrift service definition
    :param hosts:
        [(host, port), (host, port)]

        => self.hosts {(host, port): connections}
    :param pool_size: client pool size
    :param timeout: socket timeout in seconds
    :param check_time: time interval to check failed connections
    :param client_version: the version of the client
    """
    def __init__(self, client_name, service, hosts=None, pool_size=30,
                 timeout=30, check_time=10, client_version='-'):
        self.meta = {'client_name': client_name,
                     'client_version': client_version}
        self.hosts = {item: 0 for item in hosts or []}
        self._failed_hosts = {}
        self.timeout = timeout * 1000
        self.service = service
        self.check_time = check_time
        self.clients = collections.deque(maxlen=pool_size)

    def _is_failed(self, host):
        return host in self._failed_hosts

    def _get_failed_host(self):
        for host, t in list(self._failed_hosts.items()):
            if host not in self.hosts:
                self._failed_hosts.pop(host)
                continue

            if time.time() - t > self.check_time:
                self._failed_hosts.pop(host)
                return host

    def choose_host(self):
        """Choose a host using least connections
        """
        hosts = [(h, c) for h, c in self.hosts.items()
                 if not self._is_failed(h)]
        if not hosts:
            raise RuntimeError('No active server available')

        min_conns = min(c for _, c in hosts)
        hosts = [h for h, c in hosts if c == min_conns]
        return random.choice(hosts)

    def _create_client(self):
        host = self._get_failed_host()
        if not host:
            host = self.choose_host()
        sock = TSocket(*host)
        sock.set_timeout(self.timeout)
        trans = TBufferedTransport(sock)
        try:
            trans.open()
            # Increase connection count
            if host in self.hosts:
                self.hosts[host] += 1
        except TTransportException as e:
            self._failed_hosts[host] = time.time()
            return self._create_client()

        proto = TBinaryProtocol(trans)
        return Client(self.service, proto, meta=self.meta), host

    def _close_client(self, client, host):
        client.close()
        if host in self.hosts:
            self.hosts[host] -= 1

    def pick_client(self):
        """Pick a client from clients pool
        """
        if self.clients:
            client, host = self.clients.popleft()
            if self.is_client_health(client):
                return client, host
            self._close_client(client, host)
        return self._create_client()

    @staticmethod
    def is_client_health(client):
        """Check health of the client
        """
        return client._health_check()

    def close(self):
        """Close all client in the pool
        """
        for client, host in self.clients:
            self._close_client(client, host)

    def _put_back(self, client, host):
        """Put the client back to the pool
        """
        if len(self.clients) == self.clients.maxlen:
            self._close_client(*self.clients.popleft())
        self.clients.append((client, host))

    @contextlib.contextmanager
    def client_ctx(self):
        """Get a client and put back to pool after used
        """
        client, host = self.pick_client()

        try:
            yield client
        except (TTransportException, socket.error):
            self._close_client(client, host)
            raise
        else:
            self._put_back(client, host)


class _PoolDict(dict):
    settings_schema = schema.Schema({
        str: {
            'service_name': str,
            'thrift_file': os.path.exists,
            schema.Optional('pool_size'): int,
            schema.Optional('timeout'): int,
            schema.Optional('check_time'): int,
            str: object
        }
    })

    def __init__(self, pool_size=30, timeout=30, check_time=10):
        self.pool_size = pool_size
        self.timeout = timeout
        self.check_time = check_time
        self.settings = config.settings['CLIENT_SETTINGS']
        # Validate settings
        try:
            self.settings_schema.validate(self.settings)
        except schema.SchemaError as e:
            raise RuntimeError('Invalid `CLIENT_SETTINGS`: {}'.format(e))

    def _get_pool(self, key):
        client_name = config.app_name
        client_version = config.version or '-'
        conf = self.settings[key]
        service_name = conf['service_name']
        module_name = '{}_thrift'.format(service_name)
        thrift = load(conf['thrift_file'], module_name)
        service = getattr(thrift, service_name)

        pool = Pool(client_name, service,
                    pool_size=conf.get('pool_size', self.pool_size),
                    timeout=conf.get('timeout', self.timeout),
                    check_time=conf.get('check_time', self.check_time),
                    client_version=client_version)

        if 'hosts_class' not in conf:
            conf['hosts_class'] = 'takumi_client.hosts.ListHosts'
        hosts = load_class(conf['hosts_class'])(conf, pool.hosts)
        hosts.update()
        return pool

    def __getitem__(self, key):
        pool = self.get(key)
        if not pool:
            pool = self._get_pool(key)
            self[key] = pool
        return pool


clients = _PoolDict()
