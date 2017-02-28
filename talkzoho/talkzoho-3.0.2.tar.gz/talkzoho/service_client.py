from tornado.httpclient import AsyncHTTPClient
from talkzoho.regions import US


class ServiceClient:

    def __init__(self, *, auth_token: str, region: str=US):
        self.auth_token = auth_token
        self.region     = region

    @property
    def http_client(self):
        return AsyncHTTPClient()
