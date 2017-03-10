# coding=utf-8
import logging.config
import unittest

from dsn_redis import RedisProxy
from dsn_redis import StrictRedisBuilder


class PrototypesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.config.fileConfig('logging.conf')

    def setUp(self):
        builder = StrictRedisBuilder()
        redis = builder.build()
        self.proxy = RedisProxy(redis)

    def test_hash_map(self):
        try:
            hmap = self.proxy.get_hash_map('hashmap')
            hmap['a'] = 'a'
            hmap['b'] = 'b'
            hmap['c'] = 1
            hmap.expire(1200)
            print(self.proxy.delete('hashmap'))
            self.assertFalse(self.proxy.exists('hashmap'))
        except Exception as e:
            print(e)
            self.fail()
