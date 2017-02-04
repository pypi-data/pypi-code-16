import time

import happybase
import mock
import pytest

from cacheutils.hbase import HBaseTTLCache


class TestHBaseTTLCache(object):
    @pytest.mark.usage
    def test_usage(self):
        TABLE = 'hbasettlcache'
        conn = happybase.Connection(host='localhost', port=9090, timeout=10000)
        if TABLE in conn.tables():
            conn.delete_table(TABLE, disable=True)
        conn.create_table(TABLE, {'f': {'max_versions': 1,
                                        'block_cache_enabled': 1}})
        table = conn.table(TABLE)
        cache = HBaseTTLCache(table, 1, maxsize=10)
        for value in range(11):
            cache[str(value)] = {'f:value': str(value)}
        time.sleep(2)
        with pytest.raises(KeyError):
            # Is expired, also triggers expiration on the entire
            # data structure
            cache['0']
        assert list(table.scan()) == [('0', {'f:value': '0'})]
        conn.close()

    def test___init____normal(self):
        table, ttl, maxsize = mock.Mock(), 0, 0
        cache = HBaseTTLCache(table, ttl, maxsize=maxsize)
        assert cache.table is table
        assert cache.ttl is ttl
        assert cache.maxsize is maxsize

    def test___init____no_arguments(self):
        with pytest.raises(TypeError):
            HBaseTTLCache()

    def test___init____ttl_not_int(self):
        table, ttl, maxsize = mock.Mock(), None, 0
        with pytest.raises(TypeError):
            HBaseTTLCache(table, ttl, maxsize=maxsize)

    def test___init____maxsize_not_int(self):
        table, ttl, maxsize = mock.Mock(), 0, None
        with pytest.raises(TypeError):
            HBaseTTLCache(table, ttl, maxsize=maxsize)

    def test___missing__return_value(self):
        key, value = 'key', 'value'
        timestamp, ttl = int(time.time() * 1000), 1
        table = mock.Mock()
        table.row.return_value = {'f:col': (value, timestamp)}
        cache = HBaseTTLCache(table, ttl, maxsize=0)
        assert cache._Cache__missing(key) == {'f:col': value}
        assert cache._TTLCache__links[key].expire == timestamp / 1000 + ttl
        assert key in cache._HBaseTTLCache__keep_expire
        table.row.assert_called_once_with('key', include_timestamp=True)

    def test___missing__keyerror(self):
        key = 'key'
        table = mock.Mock()
        table.row.return_value = {}
        cache = HBaseTTLCache(table, 0, maxsize=0)
        with pytest.raises(KeyError):
            cache._Cache__missing(key)
        assert key not in cache._TTLCache__links
        assert key not in cache._HBaseTTLCache__keep_expire
        table.row.assert_called_once_with('key', include_timestamp=True)

    def test_popitem__keyerror(self):
        table = mock.Mock()
        cache = HBaseTTLCache(table, 0, maxsize=0)
        with pytest.raises(KeyError):
            cache.popitem()
        table.assert_not_called()

    def test_popitem(self):
        key, value = 'key', 'value'
        table = mock.Mock()
        cache = HBaseTTLCache(table, 1, maxsize=1)
        cache._store_item = mock.Mock(autospec=True)
        cache[key] = value
        assert cache.popitem() == (key, value)
        cache._store_item.assert_called_once_with(key, value)

    def test__store_item__no_timestamp(self):
        key, value, timestamp, ttl = 'key', 'value', 10, 1
        table = mock.Mock()
        cache = HBaseTTLCache(table, ttl, maxsize=0)
        link = mock.Mock()
        link.expire = timestamp + ttl
        cache._TTLCache__links[key] = link
        assert cache._store_item(key, value) is True
        table.put.assert_called_once_with(key, value,
                                          timestamp=timestamp * 1000)

    def test__store_item__timestamp(self):
        key, value = 'key', 'value'
        table = mock.Mock()
        cache = HBaseTTLCache(table, 0, maxsize=0)
        assert cache._store_item(key, value) is True
        table.put.assert_called_once_with(key, value, timestamp=None)

    @mock.patch('cacheutils.hbase.six.iteritems')
    def test_flush(self, mocked_six_iteritems):
        key, value = 'key', 'value'
        mocked_six_iteritems.return_value = ((key, value), )
        table = mock.Mock()
        cache = HBaseTTLCache(table, 0, maxsize=0)
        cache._store_item = mock.Mock(autospec=True)
        assert cache.flush() is True
        cache._store_item.assert_called_once_with(key, value)

    def test_close__flush(self):
        table = mock.Mock()
        cache = HBaseTTLCache(table, 0, maxsize=0)
        cache.flush = mock.Mock(autospec=True)
        assert cache.close(flush=True) is True
        cache.flush.assert_called_once_with()

    def test_close__no_flush(self):
        table = mock.Mock()
        cache = HBaseTTLCache(table, 0, maxsize=0)
        cache.flush = mock.Mock(autospec=True)
        assert cache.close(flush=False) is True
        cache.flush.assert_not_called()

    def test___setitem______keep_expire(self):
        key, value, expire = 'key', 'value', 100
        table = mock.Mock()
        cache = HBaseTTLCache(table, 0, maxsize=1)
        cache._HBaseTTLCache__keep_expire.add(key)
        _link = mock.Mock()
        _link.expire = expire
        cache._TTLCache__links[key] = _link
        cache.__setitem__(key, value)
        assert cache._TTLCache__links[key].expire == expire

    def test___setitem____no__keep_expire(self):
        key, value, expire = 'key', 'value', time.time()
        table = mock.Mock()
        cache = HBaseTTLCache(table, 0, maxsize=1)
        cache.__setitem__(key, value)
        assert cache._TTLCache__links[key].expire >= expire
