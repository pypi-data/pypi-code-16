# -*- coding: utf8 -*-

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import time
import calendar
import jwt
import base64

try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus


class GeoFluent(object):

    EXPIRATION_TIME = 8

    def __init__(self, key, secret, base="https://api.geofluent.com/Translation", version=3):
        self.key = key
        self.secret = secret
        self.base = base
        self.version = version
        self._generate_token()

    def _generate_token(self):
        iat = calendar.timegm(time.gmtime())
        self.expiration = iat + 8*60*60
        claims = {
            "sub": self.key,
            "iat": iat,
            "exp": self.expiration
        }
        self.token = jwt.encode(claims, base64.b64decode(self.secret), algorithm='HS256').decode("UTF-8")
        self.headers = {
            "User-Agent":  "GeoFluent Python Client",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer %s" % self.token
        }

    def health_check(method):
        def check_expiration(self, *args):
            if calendar.timegm(time.gmtime()) > self.expiration:
                self._generate_token()
            return method(self, *args)
        return check_expiration

    def _get(self, endpoint, params={}):
        resource = "%s/v%d/%s" % (self.base, self.version, endpoint)
        #params = dict([k, quote_plus(v)] for k, v in params.items())
        if len(params) > 0:
            encoded_params = '&'.join("%s=%s" % (k, quote_plus(v)) for k, v in params.items())
            resource = "%s?%s" % (resource, encoded_params)
        return requests.get(resource, headers=self.headers)

    @health_check
    def languages(self):
        response = self._get("Languages")
        data = response.json()

        if response.status_code is not 200:
            msg = "Request to %s responded with status code %d: %s" % (response.url, response.status_code, data["error"])
            raise RuntimeError(msg)
        else:
            return data["result"]

    @health_check
    def translate(self, text, source, target):
        response = self._get("Translate", params={"text": text, "from": source, "to": target})
        data = response.json()

        if response.status_code is not 200:
            msg = "Request to %s responded with status code %d: %s" % (response.url, response.status_code, data["error"])
            raise RuntimeError(msg)
        else:
            return data["result"][0]["text"]

