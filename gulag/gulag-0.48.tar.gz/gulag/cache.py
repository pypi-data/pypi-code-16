"""
Mongo DB `capped` collection
Apparently faster than Memcached, NB. maximum pickle width

@jorjun - 4th July 2013
"""

import base64
import time
import pickle
import re
import datetime

import nosql

UTC = datetime.datetime.utcnow

MAXWIDTH = 1024 * 64  # 64K Capped collections cannot expand, so we pad records to fixed width


class Cache(nosql.MongoModel):
    """
    Cache back-end store
    == ATTRIBUTE KEY ===================
    key : Cache key
    expires_utc : Expiry time
    b64: Pickle format
    """
    db_name = "cache"
    col_name = "cache"
    capped_size = 1024 * 1024      # 1 GB
    index = [
        ("key", "is_active", "expires_utc", )
    ]

    def make_key(self, key, version=None):
        key = '%s:%s' % (version, key)
        key = re.sub(r'\$|\.', '', key)
        return key

    def add(self, key, value, timeout=None, version=None):
        return self._set(mode='add', key=key, value=value, timeout=timeout, version=version)

    def set(self, key, value, timeout=None, version=None):
        return self._set(mode='set', key=key, value=value, timeout=timeout, version=version)

    def _set(self, mode, key, value, timeout=None, version=None):
        key = self.make_key(key, version)
        if timeout is None:
            timeout = self.default_timeout

        now_utc = UTC()
        expires_utc = now_utc + datetime.timedelta(seconds=timeout)
        _bin = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        b64 = base64.encodestring(_bin).ljust(MAXWIDTH)
        rec = self.find_and_modify({'key': key},
            {'$set': {'b64': b64, 'expires_utc': expires_utc, "is_active": True}},
            upsert=True
        )
        if mode == "add":
            if rec and (not rec["is_active"] or rec["expires_utc"] <= now_utc):
                    rec = {}
            return not bool(rec)  # Returns True (added) only if a valid rec not already available

    def get(self, key, default=None, version=None):
        key = self.make_key(key, version)
        rec = self.find_one({'key': key})
        if not rec:
            return default

        if rec['expires_utc'] < UTC():
            self.delete(key=key, version=version)
            return default

        _bin = base64.decodestring(rec['b64'].strip())
        value = pickle.loads(_bin)
        return value

    def delete(self, key, version=None):
        key = self.make_key(key, version)
        self.update({'key': key}, {"$set": {"is_active": False}})

    def has_key(self, key, version=None):
        key = self.make_key(key, version)
        rec = self.find_one({'key': key, "is_active": True, 'expires_utc': {'$gt': nosql.UTC()}})
        return bool(rec)

    def clear(self):
        self.drop()


CACHE = Cache()


if __name__ == "__main__":
    cache = Cache("x", params={})
    cache.add(key="xx", value="yy", timeout=1)
    assert cache.add(key="xx", value="yy", timeout=1) == False
    assert cache.add(key="xx", value="yy", timeout=1) == False
    time.sleep(1)
    assert cache.add(key="xx", value="yy", timeout=1) == True

