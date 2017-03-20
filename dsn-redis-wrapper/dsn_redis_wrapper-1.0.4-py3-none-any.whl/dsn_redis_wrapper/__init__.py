# coding=utf-8
import logging

from redis import StrictRedis

from dsn_redis.builders import RedisBuilder
from dsn_redis.builders import StrictRedisBuilder
from dsn_redis.prototypes import RedisHashMap
from dsn_redis.prototypes import RedisNumeric
from dsn_redis.prototypes import RedisString


class RedisProxy:
    def __init__(self, redis: StrictRedis):
        assert redis, 'StrictRedis is None'
        self.__redis = redis
        self.logger = logging.getLogger('dsn.redis')

    def delete(self, name: str):
        return self.__redis.delete(name)

    def exists(self, name: str):
        return self.__redis.exists(name)

    def get_hash_map(self, name: str, auto_create=True) -> RedisHashMap:
        if not auto_create and not self.__redis.exists(name):
            raise KeyError('key not exist,%s' % name)
        return RedisHashMap(self.__redis, name)
