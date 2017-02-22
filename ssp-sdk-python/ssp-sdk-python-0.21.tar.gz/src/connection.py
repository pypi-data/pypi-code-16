# Copyright 2017 NeuStar, Inc.All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import requests

class AuthError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class RestError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class Connection:
    def __init__(self, host="api.security.biz"):
        self.host = host
        self.username = ""
        self.password = ""
        self.access_token = ""

    def auth(self, username, password):
        r1 = requests.get("https://"+self.host+"/platform/authenticate/v1", auth=(username, password))
        if r1.status_code == requests.codes.OK:
            json_body = r1.json()
            self.access_token = json_body[u'access_token']
        else:
            raise AuthError(r1.json())
        self.username = username
        self.password = password

    def _refresh(self):
        r1 = requests.get("https://"+self.host+"/platform/authenticate/v1", auth=(self.username, self.password))
        if r1.status_code == requests.codes.OK:
            json_body = r1.json()
            self.access_token = json_body[u'access_token']
        else:
            raise AuthError(r1.json())

    def _build_headers(self, content_type):
        result = {"Accept": "application/json",
                  "Authorization": "Bearer " + self.access_token}
        if content_type != "":
            result["Content-type"] = content_type
        return result

    def get(self, uri, params=None):
        if params is None:
            params = {}
        return self._do_call(uri, "GET", params=params)

    def head(self, uri, params=None):
        if params is None:
            params = {}
        return self._do_call(uri, "HEAD", params=params)

    def post_multi_part(self, uri, files):
        return self._do_call(uri, "POST", files=files, content_type="")

    def post(self, uri, json=None):
        if json is not None:
            return self._do_call(uri, "POST", body=json)
        else:
            return self._do_call(uri, "POST")

    def put(self, uri, json):
        return self._do_call(uri, "PUT", body=json)

    def patch(self, uri, json):
        return self._do_call(uri, "PATCH", body=json)

    def delete(self, uri):
        return self._do_call(uri, "DELETE")

    def _do_call(self, uri, method, params=None, body=None, retry=True, files=None, content_type="application/json"):
        # print self.host+uri
        r1 = requests.request(method, "https://"+self.host+uri, params=params, data=body, headers=self._build_headers(content_type), files=files)
        if r1.status_code == requests.codes.NO_CONTENT or r1.status_code == requests.codes.CREATED:
            return {}
        # print r1.text
        # print r1.headers
        json_body = r1.json()
        try:
            if json_body['error']:
                if json_body['error']['code'] == "AUTHENTICATION_FAILED" and retry is True:
                    self._refresh()
                    json_body = self._do_call(uri, method, params, body, False)
                else:
                    pass
        except KeyError:
            pass
        return json_body
