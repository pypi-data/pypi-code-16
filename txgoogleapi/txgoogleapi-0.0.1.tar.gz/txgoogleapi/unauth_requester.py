import json
import urllib
from twisted.internet import defer
from twisted.web.client import getPage


class UnauthRequester(object):
    def __init__(self):
        pass

    @defer.inlineCallbacks
    def __call__(self, url, method, query, body=None):
        if query is not None:
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
