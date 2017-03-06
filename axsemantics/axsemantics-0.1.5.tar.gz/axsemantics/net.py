import os
import time
from contextlib import closing

import click
import requests

from axsemantics import constants
from axsemantics.errors import (
    APIConnectionError,
    APIError,
)


def file_chunker(filename, chunksize):
    with open(filename, 'rb') as f:
        while True:
            buf = f.read(chunksize)
            if buf:
                yield buf
            else:
                break


class RequestHandler:
    def __init__(self, token=None, api_base=None):
        self.base = api_base or constants.API_BASE
        self.token = token

    def request(self, method, url, params, user_headers=None, stream=False, parse_json=True):
        url = '{}{}'.format(self.base, url)
        token = self.token  # or constants.API_TOKEN

        if method in ('get', 'delete') and params:
            url += self.encode_params(params)

        headers = {
            'User-Agent': 'AXSemantics Python Client',
            'Content-Type': 'application/json',
        }
        if token:
            if len(token) == 40:
                # old style tokens
                headers.update({'Authorization': 'Token {}'.format(token)})
            else:
                # new style tokens
                headers.update({'Authorization': 'JWT {}'.format(token)})

        if user_headers:
            headers.update(user_headers)

        if constants.DEBUG:
            print('Sending {} request to {}.'.format(method, url))

        try:
            result = self.request_and_raise(method, url, headers, params, False)
        except APIConnectionError:
            if constants.DEBUG:
                print('Request failed, sleeping for 5 seconds and retrying ...')
            time.sleep(5)
            result = self.request_and_raise(method, url, headers, params, False)
        if stream:
            return result
        else:
            if parse_json:
                return result.json()
            else:
                return result.content

    def request_and_raise(self, method, url, headers, params, stream):
        try:
            if method == 'post':
                if stream:
                    result = requests.post(url, headers=headers, data=params, timeout=30, stream=stream)
                else:
                    result = requests.post(url, headers=headers, json=params, timeout=30, stream=stream)
            elif method == 'put':
                result = requests.put(url, headers=headers, json=params, timeout=30, stream=stream)
            else:
                result = requests.request(method, url, headers=headers, timeout=30, stream=stream)

            result.raise_for_status()
            return result

        except (requests.Timeout, requests.ConnectionError, requests.exceptions.ReadTimeout):
            raise APIConnectionError

        except requests.HTTPError:
            if constants.DEBUG:
                print('Got unexpected reponse with status {}.'.format(result.status_code))
                print('Content: {}'.format(result.content))
            raise APIError(result)


    def download_with_progressbar(self, url, filename=None, label=None):
        with closing(self.request(method='get', url=url, params=None, stream=True)) as rq:
            if filename is None:
                splits = url.rsplit('/')
                # for /v1/blah.ext => blah.ext
                filename = splits[-1]
                if not filename:
                    # for /v1/blah/ => blah
                    filename = splits[-2]
            if label is None:
                label = filename
            chunksize = 1024
            totalsize = int(rq.headers.get('Content-Length', '0').strip())
            kwargs = {
                'show_eta': True,
                'show_percent': True,
                'show_pos': True,
            }
            if label:
                kwargs['label'] = label
            if totalsize > 0:
                kwargs['length'] = int(totalsize / chunksize)

            with click.progressbar(rq.iter_content(chunksize), **kwargs) as bar:
                with open(filename, 'wb') as f:
                    for buf in bar:
                        if buf:
                            f.write(buf)


    def upload_with_progressbar(self, url, filename):
        chunksize = 1024

        totalsize = os.path.getsize(filename)
        kwargs = {
            'show_eta': True,
            'show_percent': True,
            'show_pos': True,
            'length': int(totalsize / chunksize),
            'label': 'Uploading {}'.format(os.path.basename(filename)),
        }
        with click.progressbar(file_chunker(filename, chunksize), **kwargs) as bar:
            self.request(method='post', url=url, data=bar, stream=True)


    def encode_params(self, params):
        if isinstance(params, dict):
            return '?' + self._dict_encode(params)
        if isinstance(params, list):
            return '?' + '&'.join(self._dict_encode(d) for d in params)

    def _dict_encode(self, data):
        return '&'.join(
            '{}={}'.format(key, value)
            for key, value in data.items()
        )
