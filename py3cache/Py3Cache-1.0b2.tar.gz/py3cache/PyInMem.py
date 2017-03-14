# -*- coding: utf-8 -*-

"""
Python Mem Cache with cache evict callback
"""
import configparser
import os
from time import time

from py3cache import pylru


class PyInMem:

    LASTACCESS = "last"
    regions = {}
    cacheexpire = {}
    cachetime = {}

    def __init__(self, opts, callback=None):
        self.callback = callback
        options = dict(opts)
        for region in options['regions'].split(','):
            cachesize = int(options.get("cache." + region + ".max_entries"))
            self.regions[region] = pylru.lrucache(cachesize)
            self.cachetime[region] = {}
            cexpire = int(options.get("cache." + region + ".expire"))
            self.cacheexpire[region] = cexpire
            print("build cache {0}[{1},{2}] ok.".format(region, cachesize, cexpire))

    def get(self, region, key):
        ctime = self.cachetime[region].get(key)
        if ctime is None:
            return None
        if (ctime.expire > 0) and (time() - ctime.begin > ctime.expire):
            self.evict(region, key)
            return None
        ctime.last = time()
        self.cachetime[region][key] = ctime
        return self.regions[region].get(key)

    def set(self, region, key, value):
        expire = self.cacheexpire.get(region)
        expire = 0 if expire is None else expire

        ctime = PyInMem.CacheTime(begin=time(), expire=expire, last=time())
        self.cachetime[region][key] = ctime

        cache = self.regions[region]
        if cache is None:
            raise KeyError("Unknown cache region {0}".format(region))

        cache[key] = value

    def _evict(self, region, key):
        try:
            del self.regions[region][key]
        except KeyError as ke:
            pass
        try:
            del self.cachetime[region][key]
        except KeyError as ke:
            pass

    def evict(self, region, key):
        self._evict(region, key)
        if self.callback is not None:
            self.callback('evict', region, key)

    def _clear(self, region):
        self.regions[region].clear()
        self.cachetime[region].clear()

    def clear(self, region):
        self._clear(region)
        if self.callback is not None:
            self.callback('clear', region)

    class CacheTime:

        def __init__(self, begin=0, expire=0, last=0):
            self.begin = begin
            self.expire = expire
            self.last = last

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.optionxform = str  # 保留配置文件key的大小写设定
    config_path = os.path.join(os.path.split(os.path.realpath(__file__))[0],"config.ini")
    config.read(config_path)

    opts = config.items('memory')
    pm = PyInMem(opts)

    for x in range(1, 10000):
        pm.set("Users", x, {'name': 'Winter Lau {0}'.format(x), "age": x})

    pm.evict("Users", 4)

    print(pm.get("Users", 1))
    print(pm.get("Users", 9999))

    pm.clear("Users")
