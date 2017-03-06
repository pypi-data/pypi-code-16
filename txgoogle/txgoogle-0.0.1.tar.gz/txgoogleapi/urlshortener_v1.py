from txgoogleapi.base import GoogleApi, GoogleApiEndPoint, ONEOF


class URL(GoogleApiEndPoint):
    _url = '/url'
    _methods = {
        'insert': {
            'method': 'POST',
        },
        'get': {
            'method': 'GET',
            'required': {
                'shortUrl': str,
            },
            'optional': {
                'projection': ONEOF('FULL', 'ANALYTICS_CLICKS', 'ANALYTICS_TOP_STRINGS'),
            },
        },
        'list': {
            'method': 'GET',
            'optional': {
                'start-token': str,
                'projection': ONEOF('FULL', 'ANALYTICS_CLICKS'),
            },
        },
    }


class UrlshortenerV1(GoogleApi):
    _url = '/urlshortener/v1'
    _apis = {
        'url': URL,
    }
