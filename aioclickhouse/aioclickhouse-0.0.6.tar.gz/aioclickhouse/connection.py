import warnings

from aiohttp import ClientSession, ClientResponseError
from urllib.parse import urlencode

from aioclickhouse.error import DatabaseException
from aioclickhouse.response import Response


class Connection(object):
    def __init__(self, host, port, database='default', user=None, password=None, loop=None):
        super().__init__()
        self.loop = loop
        self.session = ClientSession(loop=self.loop)
        self.database = database
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self._url = self._get_url()

    async def execute(self, request):
        try:
            resp = await self.session.post(self._url, data=request)
        except ClientResponseError as e:
            raise DatabaseException(e, request)
        resp_body = await resp.text()
        if not self._is_ok_response(resp):
            raise DatabaseException(resp_body)

        return Response(resp_body)

    @staticmethod
    def _is_ok_response(response):
        return 200 <= response.status < 300

    def _get_url(self):
        base_url = 'http://%(host)s:%(port)d/' % {
            'host': self.host,
            'port': self.port,
        }

        params = {'database': self.database, }

        if self.user:
            params['user'] = self.user
        if self.password:
            params['password'] = self.password

        return base_url + '?' + urlencode(params)

    def close(self):
        self.session.close()

    def reconnect(self):
        self.session.close()
        self.session = ClientSession(loop=self.loop)

    def __enter__(self):
        warnings.warn("Use async with instead", DeprecationWarning)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
