#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>

"""
import json

import requests
import requests.exceptions

from cdumay_rest_client.exceptions import InternalServerError
from cdumay_rest_client.exceptions import MisdirectedRequest
from cdumay_rest_client.exceptions import from_response


class RESTClient(object):
    """RestClient"""

    def __init__(
            self, server, timeout=10, headers=None, username=None,
            password=None, ssl_verify=True):
        self.server = server
        self.timeout = timeout
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        if headers:
            self.headers.update(headers)

        self.auth = (username, password) if username and password else None
        self.ssl_verify = ssl_verify

    def __repr__(self):
        return 'Connection: %s' % self.server

    @staticmethod
    def _request_wrapper(**kwargs):
        return requests.request(**kwargs)

    def do_request(self, method, path, params=None, data=None, headers=None, timeout=None):
        url = ''.join([self.server.rstrip('/'), path])
        if not headers:
            headers = dict()
        headers.update(self.headers)
        try:
            response = self._request_wrapper(
                method=method,
                url=url,
                params=params,
                data=json.dumps(data) if data else None,
                auth=self.auth,
                headers=headers,
                timeout=timeout or self.timeout,
                verify=self.ssl_verify
            )
        except requests.exceptions.RequestException as e:
            raise InternalServerError(
                message=getattr(e, 'message', "Internal Server Error"),
                extra=dict(url=url)
            )

        if response is None:
            raise MisdirectedRequest(extra=dict(url=url))

        if response.status_code >= 300:
            raise from_response(response, url)

        # noinspection PyBroadException
        try:
            return response.json()
        except:
            return response.text
