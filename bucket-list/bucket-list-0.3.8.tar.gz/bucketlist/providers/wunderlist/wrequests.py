import sys
import json
import requests

from bucketlist import appconfig
from bucketlist.errors import BucketlistError


def raise_if_error(resp):
    if resp is None:
        raise BucketlistError("Failed to get a valid response from" +
                              " Wunderlist. Please try after some time.")

    if 'error' in resp:
        if 'authentication' in resp['error'] and \
                'missing' in resp['error']['authentication']:
            raise BucketlistError("Invalid access token or client id.")
        raise BucketlistError(resp['error']['message'],
                              error_code=resp['error'].get('type'))

    if 'invalid_request' in resp:
        raise BucketlistError("Invalid access token or client id.")


class WRequests:

    MAX_RETRIES = 3

    @staticmethod
    def get(*args, **kwargs):
        headers = {
            'X-Access-Token': appconfig.get('provider_config', 'access-token'),
            'X-Client-ID': appconfig.get('provider_config', 'client-id')
        }

        resp = None
        for _ in range(WRequests.MAX_RETRIES):
            try:
                resp = requests.get(*args, headers=headers, **kwargs).json()
            except json.decoder.JSONDecodeError:
                resp = None
            else:
                break

        raise_if_error(resp)
        return resp

    @staticmethod
    def post(*args, **kwargs):
        headers = {
            'X-Access-Token': appconfig.get('provider_config', 'access-token'),
            'X-Client-ID': appconfig.get('provider_config', 'client-id')
        }

        resp = None
        for _ in range(WRequests.MAX_RETRIES):
            try:
                resp = requests.post(*args, headers=headers, **kwargs).json()
            except json.decoder.JSONDecodeError:
                resp = None
            else:
                break

        raise_if_error(resp)
        return resp

    @staticmethod
    def patch(*args, **kwargs):
        headers = {
            'X-Access-Token': appconfig.get('provider_config', 'access-token'),
            'X-Client-ID': appconfig.get('provider_config', 'client-id')
        }

        resp = None
        for _ in range(WRequests.MAX_RETRIES):
            try:
                resp = requests.patch(*args, headers=headers, **kwargs).json()
            except json.decoder.JSONDecodeError:
                resp = None
            else:
                break

        raise_if_error(resp)
        return resp

    @staticmethod
    def delete(*args, **kwargs):
        headers = {
            'X-Access-Token': appconfig.get('provider_config', 'access-token'),
            'X-Client-ID': appconfig.get('provider_config', 'client-id')
        }

        resp = requests.delete(*args, headers=headers, **kwargs)
        return resp.status_code == 204
