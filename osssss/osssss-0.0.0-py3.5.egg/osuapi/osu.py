try:
    import asyncio
except ImportError:
    pass
from .model import User, Score, JsonList
from . import endpoints


class OsuApi:
    def __init__(self, connector, key):
        """
        Pass requests or aiohttp or anything that implements get (session, etc)
        """
        self.connector = connector
        self.key = key

        self._process = self._process_sync
        try:
            if asyncio.iscoroutine(connector.get):
                self._process = self._process_async
        except NameError:
            pass

    def _create_request(self, endpoint, data):
        return self.connector.get(endpoint, params=data)

    async def _process_async(self, endpoint, data, type_):
        resp = await self._create_request(endpoint, data)
        data = await resp.json()
        return type_(data)

    def _process_sync(self, endpoint, data, type_):
        resp = self._create_request(endpoint, data)
        data = resp.json()
        return type_(data)

    def get_user(self, username, *, type_="string", mode=0):
        return self._process(endpoints.USER, dict(
            k=self.key,
            u=username,
            type=type_,
            m=mode
            ), JsonList(User))

    def get_user_best(self, username, *, type_="string", mode=0):
        return self._process(endpoints.USER_BEST, dict(
            k=self.key,
            u=username,
            type=type_,
            m=mode
            ), JsonList(Score))
