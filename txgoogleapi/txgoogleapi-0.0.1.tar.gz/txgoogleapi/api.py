from txgoogleapi.urlshortener_v1 import UrlshortenerV1
from txgoogleapi.youtube_v3 import YoutubeV3


class Google(object):
    _url = 'https://www.googleapis.com'
    _apis = {
        'youtube': YoutubeV3,
        'urlshortener': UrlshortenerV1,
    }

    def __init__(self, requester):
        self._requester = requester

    def __getattr__(self, item):
        api = self._apis[item](self)
        setattr(self, item, api)
        return api

    def request(self, url, method, query, body):
        return self._requester(self._url + url, method, query, body)
