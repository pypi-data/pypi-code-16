from pastry.pastry_client import PastryClient


class Base(object):
    _base_url = None

    @classmethod
    def base_url(cls):
        if not cls._base_url:
            raise ValueError('Base url has not been set of this resource')
        return cls._base_url

    @classmethod
    def index(cls):
        return PastryClient.call(cls.base_url())
