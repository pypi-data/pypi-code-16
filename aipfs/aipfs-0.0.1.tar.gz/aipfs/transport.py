import asyncio
import aiohttp


class AsyncHTTP(object):

    def __init__(self, loop=None, base_url=""):
        self.loop = loop or asyncio.get_event_loop()
        self.responses = {}
        self.client = aiohttp.ClientSession
        self.base_url = base_url
        self.sess = None

    @asyncio.coroutine
    def request(self, method, endpoint, **kwargs):
        """Requests to ipfs daemon

        """
        if not self.sess:
            self.sess = self.client(loop=self.loop)

        url = self.endpoint(endpoint)
        self.responses[url] = yield from self.sess.request(method=method, url=url, **kwargs)
        return self.responses[url]

    def endpoint(self, endpoint) -> str:
        """Get proper url"""
        return self.base_url + endpoint if self.base_url else endpoint

    def __enter__(self):
        """Enter context manager"""
        return self

    def __exit__(self, *args):
        """Close context manager"""
        self.close()

    def close(self):
        """Close session and all requests bucket"""
        if self.sess:
            self.sess.close()
        for v in self.responses.values():
            v.close()
