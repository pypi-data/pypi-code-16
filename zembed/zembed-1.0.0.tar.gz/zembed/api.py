import requests
from urllib.parse import urlencode
from zembed.exceptions import ZembedException


class API:
    _api_key = None
    _base_url = 'http://35.162.233.79'

    def __init__(self):
        self._api_key = ''

    def get_embed(self, url):
        return self._get('{}/{}'.format(self._base_url, 'crawler'), {'url': urlencode(url)})

    @staticmethod
    def _get(url, params=None, **kwargs):
        result = requests.get(url, params=params, **kwargs)
        _response = result.json()

        if _response and 'error' in _response:
            raise ZembedException('')

        if result.status_code != 200:
            raise ZembedException(result.status_code, result.reason, result)

        return result

    @staticmethod
    def response(response):
        return response.json()
