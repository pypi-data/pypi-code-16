#!/usr/bin/env python

"""
Deep-Compute peoplegraph client.
"""

import sys
import hmac
import json
import base64
import hashlib
import argparse
import requests
import datetime
import dateutil.tz
from time import sleep
from urlparse import urljoin
from requests.auth import AuthBase

class APICallException(Exception): pass
class APICallConnectionError(APICallException): pass
class APICallTimeout(APICallException): pass
class APICallBadResponse(APICallException): pass

class APICallFailed(APICallException):
    def __init__(self, url, message=''):
        self.url = url
        self.message = message

    def __str__(self):
        return 'APICallFailed(url={}, message={})'.format(self.url, self.message)

    __repr__ = __str__
    __unicode__ = __str__


class HmacAuth(AuthBase):
    '''
    Adapted from https://github.com/bazaarvoice/python-hmac-auth
    '''

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        ts = datetime.datetime.now(dateutil.tz.tzutc()).isoformat() # ISO8601

        msg = [self.api_key, request.method, ts, request.path_url]
        if request.body:
            msg.append(request.body)
        msg = '\n'.join(msg)

        digest = hmac.new(self.secret_key, msg, hashlib.sha256).digest()
        sig = base64.standard_b64encode(digest).strip()

        request.headers['Authorization'] = 'RQST %s:%s' % (self.api_key, sig)
        request.headers['X-Auth-Timestamp'] = ts

        return request

class Client(object):
    """
    Peoplegraph api client
    """
    # TODO add logging
    # TODO add settings
    # TODO add multiget
    # TODO add callback

    def __init__(self, host, username, secret):
        self.host = host
        self.auth = HmacAuth(username, secret)

    def get_person(self, name, callback=None):
        """
        queries the server for a  person
        """

        url = urljoin(self.host, "/peoplegraph/api/lookup")
        params = { "name": name }
        if callback is not None:
            params['callback'] = callback

        # TODO add settings
        try:
            resp = requests.get(url, auth=self.auth, params=params).json()
        except ValueError:
            raise APICallBadResponse
        except requests.Timeout:
            raise APICallTimeout
        except requests.ConnectionError:
            raise APICallConnectionError

        success = resp['success']
        if not success:
            raise APICallFailed(url=url, message=resp.get('message', ''))

        return resp['result']
