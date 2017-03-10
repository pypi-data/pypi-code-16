# -*- coding: utf-8 -*-

import pytest
import thriftpy
import time
import mock
import socket


@pytest.fixture
def pool():
    from takumi_client.pool import Pool
    from takumi_config import config
    thrift = thriftpy.load(config.thrift_file)
    pool = Pool('test_client', thrift.PingService)
    return pool


@pytest.fixture
def mock_connect():
    with mock.patch.object(socket.socket, 'connect') as m:
        yield m


def test_is_failed(pool):
    pool._failed_hosts[('localhost', 9000)] = time.time()
    assert pool._is_failed(('localhost', 9000))
    assert not pool._is_failed(('localhost', 9001))


def test_get_failed_host(pool):
    host = 'localhost', 9000
    pool._failed_hosts[host] = time.time() - 11
    assert pool._get_failed_host() is None

    pool.hosts[host] = 0
    pool._failed_hosts[host] = time.time() - 11
    assert pool._get_failed_host() == host
    assert host not in pool._failed_hosts

    pool._failed_hosts[host] = time.time()
    assert pool._get_failed_host() is None
    assert host in pool._failed_hosts


def test_choose_host(pool):
    pool.hosts = {
        ('localhost', 1000): 1,
        ('localhost', 2000): 3,
        ('localhost', 3000): 2,
    }

    assert pool.choose_host() == ('localhost', 1000)
    pool._failed_hosts[('localhost', 1000)] = time.time()
    assert pool.choose_host() == ('localhost', 3000)

    pool._failed_hosts[('localhost', 2000)] = time.time()
    pool._failed_hosts[('localhost', 3000)] = time.time()
    with pytest.raises(RuntimeError) as e:
        pool.choose_host()
    assert str(e.value) == 'No active server available'


def test_create_client(pool, mock_connect):
    pool.hosts = {
        ('localhost', 1000): 1,
        ('localhost', 3000): 2,
    }
    pool._failed_hosts[('localhost', 1000)] = time.time() - 11
    ret = pool._create_client()
    assert ret[1] == ('localhost', 1000)
    mock_connect.assert_called_with(('localhost', 1000))
    assert pool.hosts[('localhost', 1000)] == 2


def test_close_client(pool, mock_connect):
    pool.hosts = {('localhost', 1000): 0}
    client, host = pool._create_client()

    from takumi_thrift import Client
    with mock.patch.object(Client, 'close') as mock_close:
        pool._close_client(client, host)
    mock_close.assert_called_with()
    assert pool.hosts[('localhost', 1000)] == 0


def test_close(pool, mock_connect):
    from takumi_thrift import Client
    pool.hosts = {('localhost', 1000): 0}
    client, _ = pool._create_client()
    pool._put_back(client, ('localhost', 1000))
    with mock.patch.object(Client, 'close') as mock_close:
        pool.close()
    mock_close.assert_called_with()


def test_pick_client(pool, mock_connect):
    from takumi_thrift import Client
    pool.hosts = {('localhost', 1000): 0}
    client, host = pool.pick_client()
    assert not pool.clients
    pool._put_back(client, ('localhost', 1000))
    assert pool.clients
    with mock.patch.object(Client, '_health_check') as mock_health:
        client, host = pool.pick_client()
        assert host == ('localhost', 1000)
    mock_health.assert_called_with()
    assert not pool.clients


def test_client_ctx(pool, mock_connect):
    from takumi_thrift import Client
    pool.hosts = {('localhost', 1000): 0}
    with pool.client_ctx() as c:
        assert isinstance(c, Client)
    assert pool.clients


def test_pool_manager():
    from takumi_config import config
    from takumi_client.pool import _PoolDict, Pool
    config.settings['CLIENT_SETTINGS']['test_client'] = {
        'service_name': 'test'
    }
    with pytest.raises(RuntimeError) as e:
        _PoolDict()
    assert 'Invalid `CLIENT_SETTINGS`:' in str(e.value)

    config.settings['CLIENT_SETTINGS'].pop('test_client')

    p = _PoolDict()
    assert isinstance(p['test'], Pool)
    assert list(p.keys()) == ['test']
