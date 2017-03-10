# coding=utf-8
# prototypes.py
import datetime
import logging

from redis import StrictRedis


class RedisObject:
    def __init__(self, redis: StrictRedis, name: str):
        assert redis, 'StrictRedis is None'
        assert name, 'name is None'
        self.logger = logging.getLogger('dsn.redis.prototypes')
        self._redis = redis
        self.__name = name

    @property
    def name(self):
        return self.__name

    def exists(self):
        return self._redis.exists(self.__name)

    def expire(self, time):
        return self._redis.expire(self.__name, time)

    def expire_at(self, when: datetime.datetime):
        return self._redis.expireat(self.__name, when)

    def time_to_live(self):
        return self._redis.ttl(self.__name)

    def persist(self):
        return self._redis.persist(self.__name)


class RedisHashMap(RedisObject):
    """ Hash implementation"""

    def __init__(self, redis, name: str):
        super(RedisHashMap, self).__init__(redis, name)

    def __getitem__(self, item: str):
        return self.get(item)

    def __setitem__(self, key: str, value):
        return self.set(key, value)

    def get(self, key: str):
        return self._redis.hget(self.name, key)

    def set(self, key: str, value):
        return self._redis.hset(self.name, key, value)

    def remove(self, *keys):
        return self._redis.hdel(self.name, keys)


class RedisSimpleType(RedisObject):
    """ abstract type for simple data"""

    def __init__(self, redis, name: str):
        super(RedisSimpleType, self).__init__(redis, name)

    def get(self):
        return self._redis.get(self.name)

    def set(self, value, ex=None, px=None, nx=None, xx=None):
        self._redis.set(self.name, value, ex=ex, px=px, nx=nx, xx=xx)


class RedisString(RedisSimpleType):
    def __init__(self, redis, name: str):
        super(RedisString, self).__init__(redis, name)


class RedisNumeric(RedisSimpleType):
    def __init__(self, redis, name: str):
        super(RedisNumeric, self).__init__(redis, name)

    def inc(self, amount: int = 1):
        self._redis.incr(self.name, amount=amount)

    def inc_by_float(self, amount: float = 1.0):
        self._redis.incrbyfloat(self.name, amount=amount)


class RedisSet(RedisObject):
    """ Set implementation"""

    def __init__(self, redis, name: str):
        super(RedisSet, self).__init__(redis, name)


class RedisSortedSet(RedisObject):
    """ SortedSet implementation"""

    def __init__(self, redis, name: str):
        super(RedisSortedSet, self).__init__(redis, name)


class RedisList(RedisObject):
    """ List implementation"""

    def __init__(self, redis, name: str):
        super(RedisList, self).__init__(redis, name)
