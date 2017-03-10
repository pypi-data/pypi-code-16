# coding: utf-8
# redis.py
import logging
import time
import uuid

from dsn_redis import RedisProxy
from dsn_redis.prototypes import RedisHashMap
from redis import StrictRedis

from dsn_tornado.session import Session
from dsn_tornado.session import SessionManager
from dsn_tornado.session import SessionStorageError

_DSN_SESSION_PREFIX = 'dsn_session:'
_FIELD_CREATION_TIME = 'creation_time'
_READ_ONLY_FIELDS = {_FIELD_CREATION_TIME: True}


def _get_logger():
    return logging.getLogger('dsn.tornado.session.redis')


class RedisSession(Session):
    """
    Session implementation by redis
    """

    def __init__(self, session_id: str, hashmap: RedisHashMap):
        super(RedisSession, self).__init__(session_id=session_id)
        self.logger = _get_logger()
        self._hashmap = hashmap

    def set(self, key: str, value):
        if _READ_ONLY_FIELDS.get(key, False):
            self.logger.warning('ignore read-only field:%s' % key)
            return False
        if self._hashmap.exists():
            self._hashmap[key] = value
            return True
        raise SessionStorageError('session not exists,id=%s' % self.id)

    def get(self, key: str):
        if self._hashmap.exists():
            return self._hashmap[key]
        raise SessionStorageError('session not exists,id=%s' % self.id)

    def available(self) -> bool:
        return self._hashmap.exists()

    def remove(self, key: str):
        return self._hashmap.remove(key)


class RedisSessionManager(SessionManager):
    """
    SessionManager implementation by redis
    """

    def __init__(self, redis: StrictRedis, time_to_live: int = 7200):
        super(RedisSessionManager, self).__init__(time_to_live=time_to_live)
        assert redis, 'StrictRedis is None'
        self.logger = _get_logger()
        self._proxy = RedisProxy(redis)

    def exists(self, session_id: str):
        assert session_id, 'session_id is None'
        sid = _DSN_SESSION_PREFIX + session_id
        return self._proxy.exists(sid)

    def create(self) -> Session:
        uid = str(uuid.uuid1())
        sid = _DSN_SESSION_PREFIX + uid
        if self._proxy.exists(sid):
            raise SessionStorageError('duplicate session id:%s' % uid)
        hashmap = self._proxy.get_hash_map(sid)
        stamp = int(time.time())
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug('timestamp=%d', stamp)
        hashmap[_FIELD_CREATION_TIME] = stamp
        hashmap.expire(self.time_to_live)
        return RedisSession(uid, hashmap)

    def remove(self, session_id: str):
        sid = _DSN_SESSION_PREFIX + session_id
        self._proxy.delete(sid)

    def get(self, session_id: str):
        sid = _DSN_SESSION_PREFIX + session_id
        if self._proxy.exists(sid):
            mp = self._proxy.get_hash_map(sid)
            return RedisSession(session_id, mp)
        raise SessionStorageError('session not exists,id=%s' % session_id)
