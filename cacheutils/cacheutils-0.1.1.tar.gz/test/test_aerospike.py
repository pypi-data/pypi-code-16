import time

import aerospike
import mock
import pytest

from cacheutils.aerospike import AerospikeTTLCache


class TestAerospikeTTLCache(object):
    @pytest.mark.usage
    def test_usage(self):
        NAMESPACE, SET = 'test', 'cache'
        client = aerospike.client({'hosts': [('172.17.0.4', 3000)]}).connect()

        cache = AerospikeTTLCache(client, NAMESPACE, SET, 1, maxsize=10)
        for value in range(11):
            cache[str(value)] = {'value': str(value)}
        time.sleep(2)
        with pytest.raises(KeyError):
            # Is expired, also triggers expiration on the entire
            # data structure
            cache['0']
        results = [x[2] for x in client.scan(NAMESPACE).results()]
        [x.pop('__timestamp') for x in results]  # remove timestamp
        assert results == [{'value': '0'}]
        cache['key'] = {'x': 'z'}
        cache.flush()
        assert cache['key'] == {'x': 'z'}
        client.close(flush=False)

    def test___init____normal(self):
        client, namespace, set_, ttl, maxsize = mock.Mock(), 'ns', 'set', 0, 0
        cache = AerospikeTTLCache(client, namespace, set_,
                                  ttl, maxsize=maxsize)
        assert cache.client is client
        assert cache.namespace is namespace
        assert cache.set is set_
        assert cache.ttl is ttl
        assert cache.maxsize is maxsize

    def test___init____no_arguments(self):
        with pytest.raises(TypeError):
            AerospikeTTLCache()

    def test___init____ttl_not_int(self):
        client = mock.Mock()
        with pytest.raises(TypeError):
            AerospikeTTLCache(client, 'ns', 'set', None, maxsize=0)

    def test___init____maxsize_not_int(self):
        client = mock.Mock()
        with pytest.raises(TypeError):
            AerospikeTTLCache(client, 'ns', 'set', 0, maxsize=None)

    def test___missing__return_value(self):
        key, value = 'key', {'col': 'value'}
        timestamp, ttl = time.time(), 1
        client = mock.Mock()
        client.get.return_value = (None, None,
                                   dict(__timestamp=timestamp, **value))
        cache = AerospikeTTLCache(client, 'ns', 'set', ttl, maxsize=0)
        assert cache._Cache__missing(key) == value
        assert cache._TTLCache__links[key].expire == timestamp + ttl
        assert key in cache._AerospikeTTLCache__keep_expire
        client.get.assert_called_once_with(('ns', 'set', 'key'))

    def test___missing__keyerror(self):
        key = 'key'
        client = mock.Mock()
        client.get.return_value = (None, {}, {})
        cache = AerospikeTTLCache(client, 'ns', 'set', 0, maxsize=0)
        with pytest.raises(KeyError):
            cache._Cache__missing(key)
        assert key not in cache._TTLCache__links
        assert key not in cache._AerospikeTTLCache__keep_expire
        client.get.assert_called_once_with(('ns', 'set', 'key'))

    def test_popitem__keyerror(self):
        client = mock.Mock()
        cache = AerospikeTTLCache(client, 'ns', 'set', 0, maxsize=0)
        with pytest.raises(KeyError):
            cache.popitem()
        client.assert_not_called()

    def test_popitem(self):
        key, value = 'key', 'value'
        client = mock.Mock()
        cache = AerospikeTTLCache(client, 'ns', 'set', 1, maxsize=1)
        cache._store_item = mock.Mock(autospec=True)
        cache[key] = value
        assert cache.popitem() == (key, value)
        cache._store_item.assert_called_once_with(key, value)

    def test__store_item__no_timestamp(self):
        key, value, timestamp, ttl = 'key', {'x': 'z'}, 10, 1
        client = mock.Mock()
        cache = AerospikeTTLCache(client, 'ns', 'set', ttl, maxsize=0)
        link = mock.Mock()
        link.expire = timestamp + ttl
        cache._TTLCache__links[key] = link
        assert cache._store_item(key, value) is True
        client.put.assert_called_once_with(
            ('ns', 'set', key), dict(__timestamp=timestamp, **value)
        )

    def test__store_item__timestamp(self):
        key, value = 'key', {'x': 'z'}
        client = mock.Mock()
        cache = AerospikeTTLCache(client, 'ns', 'set', 0, maxsize=0)
        assert cache._store_item(key, value) is True
        # TODO: Figure out a way to use called_once_with
        client.put.assert_called_once()

    @mock.patch('cacheutils.hbase.six.iteritems')
    def test_flush(self, mocked_six_iteritems):
        key, value = 'key', 'value'
        mocked_six_iteritems.return_value = ((key, value), )
        client = mock.Mock()
        cache = AerospikeTTLCache(client, 'ns', 'set', 0, maxsize=0)
        cache._store_item = mock.Mock(autospec=True)
        assert cache.flush() is True
        cache._store_item.assert_called_once_with(key, value)

    def test_close__flush(self):
        client = mock.Mock()
        cache = AerospikeTTLCache(client, 'ns', 'set', 0, maxsize=0)
        cache.flush = mock.Mock(autospec=True)
        assert cache.close(flush=True) is True
        cache.flush.assert_called_once_with()

    def test_close__no_flush(self):
        client = mock.Mock()
        cache = AerospikeTTLCache(client, 'ns', 'set', 0, maxsize=0)
        cache.flush = mock.Mock(autospec=True)
        assert cache.close(flush=False) is True
        cache.flush.assert_not_called()

    def test___setitem______keep_expire(self):
        key, value, expire = 'key', 'value', 100
        client = mock.Mock()
        cache = AerospikeTTLCache(client, 'ns', 'set', 0, maxsize=1)
        cache._AerospikeTTLCache__keep_expire.add(key)
        _link = mock.Mock()
        _link.expire = expire
        cache._TTLCache__links[key] = _link
        cache.__setitem__(key, value)
        assert cache._TTLCache__links[key].expire == expire

    def test___setitem____no__keep_expire(self):
        key, value, expire = 'key', 'value', time.time()
        client = mock.Mock()
        cache = AerospikeTTLCache(client, 'ns', 'set', 0, maxsize=1)
        cache.__setitem__(key, value)
        assert cache._TTLCache__links[key].expire >= expire
