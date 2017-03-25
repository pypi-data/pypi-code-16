import requests
from zembed.exceptions import ZembedException


class API:
    _api_key = None
    _base_url = 'http://35.162.233.79'

    def __init__(self, api_key=''):
        self._api_key = api_key

    @classmethod
    def get_embed(cls, url):
        return cls.response(cls._get('{}/{}'.format(cls._base_url, 'crawler'), {
            'url': url, 'api_key': cls._api_key
        }))

    @staticmethod
    def _get(url, params=None, **kwargs):
        result = requests.get(url, params=params, **kwargs)
        _response = result.json()

        if _response and 'error' in _response or result.status_code != 200:
            raise ZembedException(_response['status_code'], _response['error'], _response)

        return result

    @staticmethod
    def response(response):
        return response.json()
