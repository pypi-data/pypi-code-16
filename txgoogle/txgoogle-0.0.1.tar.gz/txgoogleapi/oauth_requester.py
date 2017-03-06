from cStringIO import StringIO
import json
import urllib
from twisted.internet import reactor, defer
from twisted.web.client import Agent, readBody, PartialDownloadError, getPage, FileBodyProducer
from twisted.web.http_headers import Headers


DEFAULT_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'


class OAuthRequester(object):
    def __init__(self, client_id=None, client_secret=None, access_token=None, refresh_token=None,
                 token_uri=DEFAULT_TOKEN_URI):
        self.agent = Agent(reactor)
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_uri = token_uri

    @defer.inlineCallbacks
    def request_access_token(self, response_code):
        data = {
            'code': response_code,
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        response = json.loads((yield getPage(
            self.token_uri,
            method='POST',
            postdata=urllib.urlencode(data),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        )))
        if 'error' in response:
            raise Exception(response.get('error_description', response['error']))

        self.access_token = response.get('access_token').encode('utf-8')
        self.refresh_token = response.get('refresh_token').encode('utf-8')

    @defer.inlineCallbacks
    def __call__(self, url, method, query, body=None):
        if query is not None:
            url += '?' + urllib.urlencode(query)

        if body is not None:
            body = FileBodyProducer(StringIO(json.dumps(body)))

        tries = 2
        while tries:
            tries -= 1
            response, response_body = yield self._request(url, method, body)

            if response.code == 200:
                defer.returnValue(response_body)
            elif response.code == 401:
                yield self._refresh_access_token()
                continue
            else:
                raise Exception('API returned %d %s' % (response.code, response.phrase))
        raise Exception('API authentication repeatedly failed')

    @defer.inlineCallbacks
    def _request(self, url, method, body):
        response = yield self.agent.request(
            method,
            url,
            Headers({
               'User-Agent': ['txgoogleapi'],
               'Content-Type': ['application/json'],
               'Authorization': ['Bearer %s' % self.access_token]
            }),
            body,
        )

        try:
            body = yield readBody(response)
        except PartialDownloadError as e:
            body = e.response

        content_type_headers = response.headers.getRawHeaders('content-type')
        for ct in content_type_headers:
            if ct.split(';')[0].lower() == 'application/json':
                body = json.loads(body)

        defer.returnValue((response, body))

    @defer.inlineCallbacks
    def _refresh_access_token(self):
        body = json.loads((yield getPage(
            self.token_uri,
            method='POST',
            postdata=urllib.urlencode({
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
            }),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        )))

        self.access_token = body['access_token'].encode('utf-8')
