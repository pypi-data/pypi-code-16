"""Work with REST API of SendPulse."""
# coding: utf-8

import json
import base64
import urllib.parse as url_parse

import requests


class Client:
    """Class for work with REST API of SendPulse."""
    def __init__(self, key, secret, token=None, base_url=None):
        self.base_url = base_url or 'https://api.sendpulse.com'
        self.key = key
        self.secret = secret
        self.token = token
        self.token_type = None
        self.expires_in = None
        self.headers = None

        self.get_token()

    def send_request(self, url, params=None, method='POST'):
        """Send a request."""
        headers = {'Authorization': '{} {}'.format(
            self.token_type, self.token)}
        url = url_parse.urljoin(self.base_url, url)

        if method == 'POST':
            return requests.post(url, headers=headers, data=params)
        elif method == 'GET':
            return self.__response(requests.get(url, headers=headers))
        else:
            raise NotImplementedError('Unknown method')

    def get_token(self):
        """Getting the token."""
        url = url_parse.urljoin(self.base_url, 'oauth/access_token')
        data = {
            'client_secret': self.secret,
            'client_id': self.key,
            'grant_type': 'client_credentials'
        }
        result = requests.post(url, data=data)

        if result.status_code == 200:
            self.token = result.json().get('access_token')
            self.token_type = result.json().get('token_type')
            self.expires_in = result.json().get('expires_in')
            return result.json()
        else:
            raise AssertionError('Getting token is failed')

    def get_domains(self):
        """Getting a list of domains."""

        return self.send_request('smtp/domains', method='GET')

    def smtp_send_email(self, email):
        """https://sendpulse.com/ru/integrations/api#send-email-smtp"""
        url = 'smtp/emails'
        email['html'] = self.__encode_html(email.get('html'))

        return self.send_request(url, {'email': json.dumps(email)})

    @staticmethod
    def __response(response):
        """Processing a response."""

        if response.status_code == 200:
            return response.json()

        return {}

    @staticmethod
    def __encode_html(string):
        """Encoding string to base64 and return string."""

        return base64.b64encode(string.encode()).decode()
