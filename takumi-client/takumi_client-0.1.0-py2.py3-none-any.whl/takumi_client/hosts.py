# -*- coding: utf-8 -*-


class ListHosts(object):
    def __init__(self, conf, target):
        self.hosts = conf['hosts']
        self.target = target

    def update(self):
        for host in list(self.target.keys()):
            if host not in self.hosts:
                self.target.pop(host)

        for host in self.hosts:
            self.target.setdefault(host, 0)


class RedisHosts(ListHosts):
    def __init__(self, conf, target):
        import redis
        import gevent
        self.key = conf['redis_key']
        self.client = redis.StrictRedis.from_url(conf['redis_dsn'])
        self.sync_freq = conf.get('sync_freq', 10)
        self.target = target
        self.hosts = self._get_hosts()
        # Start sync daemon
        gevent.spawn(self._sync_daemon)

    def _get_hosts(self):
        hosts = set()
        for item in self.client.smembers(self.key):
            host, port = item.decode('utf-8').split(':')
            hosts.add((host, int(port)))
        return hosts

    def _sync_daemon(self):
        while True:
            import time
            time.sleep(self.sync_freq)
            self.hosts = self._get_hosts()
            self.update()
