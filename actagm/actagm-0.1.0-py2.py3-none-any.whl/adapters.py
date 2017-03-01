import ssl
from requests.packages.urllib3.poolmanager import PoolManager
from requests.adapters import HTTPAdapter


class Tls12HttpAdapter(HTTPAdapter):
    """"Transport adapter" that allows us to use TLSv1_2."""

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_version=ssl.PROTOCOL_TLSv1_2,
            **pool_kwargs)


# Number of times to retry idempotent commands
AGM_RETRIES = 3


class AGMAdapter(Tls12HttpAdapter):
    """"Transport adapter" for generic AGM usage."""

    def __init__(self, *args, **kwargs):
        # max retries is the 3rd input
        # def __init__(self, pool_connections=DEFAULT_POOLSIZE,
        #      pool_maxsize=DEFAULT_POOLSIZE, max_retries=DEFAULT_RETRIES,
        #      pool_block=DEFAULT_POOLBLOCK):
        if len(args) < 3 and not kwargs.get('max_retries'):
            kwargs['max_retries'] = AGM_RETRIES
        super(AGMAdapter, self).__init__(*args, **kwargs)

# alternative hardcoded monkeypatch method
# requests.adapters.DEFAULT_RETRIES = 3
