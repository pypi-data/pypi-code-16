# coding=utf-8
import logging

from abc import ABCMeta
from abc import abstractmethod
from redis import BlockingConnectionPool
from redis import Connection
from redis import StrictRedis


class RedisBuilder(metaclass=ABCMeta):
    def __init__(self):
        self.logger = logging.getLogger('dsn.redis.builders')

    @abstractmethod
    def build(self):
        pass


class StrictRedisBuilder(RedisBuilder):
    """
    StrictRedisBuilder
    """

    def __init__(self,
                 connection_class=Connection,
                 max_connections=100,
                 blocking_timeout=30):
        super(StrictRedisBuilder, self).__init__()
        self.connection_class = connection_class
        self.max_connections = max_connections
        self.blocking_timeout = blocking_timeout
        self.arguments = dict()

    def build(self) -> StrictRedis:
        self.logger.info('initializing ConnectionPool')
        pool = BlockingConnectionPool(
            connection_class=self.connection_class,
            max_connections=self.max_connections,
            timeout=self.blocking_timeout,
            **self.arguments)
        self.logger.info('building StrictRedis')
        redis = StrictRedis(connection_pool=pool)
        self.logger.debug('send ping to server')
        resp = redis.ping()
        self.logger.debug('server response: %s', resp)
        return redis
