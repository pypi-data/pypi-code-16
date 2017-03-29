import requests
import json

def open(key, host=None):
    return Baskt(key, host=host)

def create(host=None):
    return Baskt.create(host=host)

class BasktNotFoundException(Exception):
    pass

class Baskt(object):

    HOST = 'https://baskt.xyz'

    def __init__(self, key, host=None):
        self.db = {}
        self.open(key, host)

    @staticmethod
    def create(host=None, params={}):
        if host is None:
            host = Baskt.HOST
        r = requests.post(host, json=params)
        if r.status_code == requests.codes.ok:
            return r.text
        else:
            return None

    def open(self, key, host=None):
        self.host = host
        if host is None:
            self.host = Baskt.HOST
        r = requests.get('%s/%s' % (self.host, key))
        if r.status_code == requests.codes.ok:
            self.baskt_key = key
            self.db = json.loads(r.text)
        else:
            raise BasktNotFoundException()

    def get(self, key, default_value=None):
        if key in self.db:
            return self.db[key]
        return default_value

    def keys(self):
        return self.db.keys()

    def has(self, key):
        if key in self.db:
            return True
        return False

    def set(self, key, value):
        if key in self.db and self.db[key] == value:
            return
        r = requests.put('%s/%s/%s' % (self.host, self.baskt_key, key), json=value)
        if r.status_code == requests.codes.ok:
            self.db[key] = value

    def rem(self, key):
        if key in self.db:
            r = requests.delete('%s/%s/%s' % (self.host, self.baskt_key, key))
            if r.status_code == requests.codes.ok:
                del self.db[key]

    def __str__(self):
        return "<Baskt(%s)>" % self.baskt_key
