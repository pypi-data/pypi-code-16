import json
import urllib
from twisted.internet import defer
from twisted.web.client import getPage


class ApiKeyRequester(object):
    def __init__(self, api_key, user_ip=None):
        self.api_key = api_key
        self.user_ip = user_ip

    @defer.inlineCallbacks
    def __call__(self, url, method, query, body=None):
        if query is None:
            query = {}

        query['key'] = self.api_key
        if self.user_ip:
            query['userIp'] = self.user_ip

        url += '?' + urllib.urlencode(query)

        if body is not None:
            body = json.dumps(body)

        page = yield getPage(
            url,
            method=method,
            postdata=body,
            headers={
               'User-Agent': 'txgoogleapi',
               'Content-Type': 'application/json',
            },
        )

        defer.returnValue(json.loads(page))
