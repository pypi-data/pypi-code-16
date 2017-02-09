"""Provides abstraction classes and methods to access NCC's PA API."""

#    Copyright 2017 NCC Group plc
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from contextlib import contextmanager
import json
import time
from urllib.parse import urlencode, urlparse, urlunparse
import urllib3

# Suppress custom SSL certificates warning. Otherwise they're printed once per endpoint call.
urllib3.disable_warnings()

class AuthenticationError(Exception):
    pass

class PaAuth:
    """
    Authenticate with PA's Oauth.
    """
    BASE_URL = 'https://paapi.siteconfidence.co.uk'
    http = None
    username = None
    password = None
    basic_auth = None

    _auth_token = None
    _token_expiry = None

    def __init__(self, username, password, basic_auth=None, poolmanager=None):
        self.username = username
        self.password = password
        self.basic_auth = basic_auth
        if poolmanager is not None:
            self.http = poolmanager
        else:
            self.http = urllib3.PoolManager()

    @contextmanager
    def authenticate(self):
        """
        Authenticates with the PA Oauth system
        """
        if self._auth_token is None or self._token_expiry < time.time():
            self._perform_auth()

        yield self._auth_token

    def _perform_auth(self):
        if self.basic_auth is not None:
            headers = {'Authorization': 'Basic %s' % (self.basic_auth,)}
        else:
            headers = None

        response = self.http.request(
            'POST',
            '%s/authorisation/token' % (self.BASE_URL,),
            {
                'username': self.username,
                'password': self.password,
                'grant_type': 'password'
            },
            headers
        )

        if response.status == 403:
            raise AuthenticationError("Couldn't authenticate to PA API")
        elif response.status == 500:
            raise Exception("Error communicating with API server")

        data = json.loads(response.data.decode())
        self._auth_token = data['access_token']
        self._token_expiry = (time.time() - 30 + data['expires_in'])

class PaApi:
    """
    Abstraction to access the PA API
    """
    API_URL = 'https://paapi.siteconfidence.co.uk/pa/1'
    PAGE_SIZE = 1000
    auth_realm = '617523'
    auth = None
    http = None

    def __init__(self, auth, realm, poolmanager=None):
        self.auth_realm = realm
        self.auth = auth
        if poolmanager is not None:
            self.http = poolmanager
        else:
            self.http = urllib3.PoolManager()

    def _query_api(self, method, url, fields=None):
        """
        Abstracts http queries to the API
        """
        with self.auth.authenticate() as token:
            headers = {
                'Authorization': 'Bearer %s' % (token,),
                'Realm': self.auth_realm
            }
            response = self.http.request(method, url, fields, headers)
            if response.status != 200:
                raise Exception("Failed to get API data")
            return json.loads(response.data.decode())

    def _build_url(self, endpoint, params=None):
        if params is None:
            params = {}
        urlinfo = list(urlparse(self.API_URL))
        urlinfo[2] = '%s/%s' % (urlinfo[2], endpoint)
        urlinfo[4] = urlencode(params)
        return urlunparse(urlinfo)

    def get_all_jobtemplates(self):
        """
        Retrieves the list of jobTemplates for the current realm.
        """
        endpoint = self._build_url('jobTemplates', {
            'paginationPageSize': self.PAGE_SIZE
        })
        data = self._query_api('GET', endpoint)
        return data['results']

    def get_testruns_for_jobtemplate(self, jobtemplate_uri, start_date=None):
        """
        Retrieves a bunch of test runs for a specific job template.
        """
        params = {
            'jobTemplate': jobtemplate_uri,
            'paginationPageSize': self.PAGE_SIZE
        }
        if start_date is not None:
            params['fromDate'] = start_date
        data = self._query_api('GET', self._build_url('testruns', params))
        return data['results']

    def get_pageobjects_for_testrun(self, testrun_uri):
        """
        Retrieves pageobject data for a particular testrun.
        """
        endpoint = self._build_url('objects', {
            'testRun': testrun_uri,
            'paginationPageSize': self.PAGE_SIZE
        })
        data = self._query_api('GET', endpoint)
        return data['results']
