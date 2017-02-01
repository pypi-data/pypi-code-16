"""
Falkonry Client

Client to access Condition Prediction APIs

:copyright: (c) 2016 by Falkonry Inc.
:license: MIT, see LICENSE for more details.

"""

import json
import requests
import urllib3

"""
HttpService:
    Service to make API requests to Falkonry Service
"""


class HttpService:

    def __init__(self, host, token):
        """
        constructor
        :param host: host address of Falkonry service
        :param token: Authorization token
        """
        urllib3.disable_warnings()
        self.host  = host if host is not None else "https://service.falkonry.io"
        self.token = token if token is not None else ""

    def get(self, url):
        """
        To make a GET request to Falkonry API server
        :param url: string
        """

        response = requests.get(
            self.host + url,
            headers={
                'Authorization': 'Bearer ' + self.token
            }
        )
        if response.status_code is 200:
            return json.loads(response.content)
        else:
            raise Exception(response.content)

    def post(self, url, entity):
        """
        To make a POST request to Falkonry API server
        :param url: string
        :param entity: Instantiated class object
        """
        response = requests.post(
            self.host + url,
            entity.to_json(),
            headers={
                "Content-Type": "application/json",
                'Authorization': 'Bearer ' + self.token
            }
        )
        if response.status_code is 201:
            return json.loads(response.content)
        else:
            raise Exception(response.content)

    def postData(self, url, data):
        """
        To make a POST request to Falkonry API server
        :param url: string
        :param entity: Instantiated class object
        """

        response = requests.post(
            self.host + url,
            data,
            headers={
                "Content-Type": "text/plain",
                'Authorization': 'Bearer ' + self.token
            }
        )
        if response.status_code is 202 or response.status_code is 200:
            return json.loads(response.content)
        else:
            raise Exception(response.content)           

    def put(self, url, entity):
        """
        To make a PUT request to Falkonry API server
        :param url: string
        :param entity: Instantiated class object
        """

        response = requests.put(
            self.host + url,
            entity.to_json(),
            headers={
                "Content-Type": "application/json",
                'Authorization': 'Bearer ' + self.token
            }
        )
        if response.status_code is 200:
            return json.loads(response.content)
        else:
            raise Exception(response.content)

    def fpost(self, url, form_data):
        """
        To make a form-data POST request to Falkonry API server
        :param url: string
        :param form_data: form-data
        """
        response = None

        if 'files' in form_data:
            response = requests.post(
                self.host + url,
                data=form_data['data'] if 'data' in form_data else {},
                files=form_data['files'] if 'files' in form_data else {},
                headers={
                    'Authorization': 'Bearer ' + self.token
                }
            )
        else:
            response = requests.post(
                self.host + url,
                data=json.dumps(form_data['data'] if 'data' in form_data else {}),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + self.token
                }
            )
        if response.status_code is 201 or response.status_code is 202:
            return json.loads(response.content)
        else:
            raise Exception(response.content)

    def delete(self, url):
        """
        To make a DELETE request to Falkonry API server
        :param url: string
        """
        response = requests.delete(
            self.host + url,
            headers={
              'Authorization': 'Bearer ' + self.token
            }
        )
        if response.status_code is 200:
            return json.loads(response.content)
        else:
            raise Exception(response.content)

    def upstream(self, url, form_data):
        """
        To make a form-data POST request to Falkonry API server using stream
        :param url: string
        :param form_data: form-data
        """
        response = requests.post(
            self.host + url,
            files=form_data['files'] if 'files' in form_data else {},
            headers={
                'Authorization': 'Bearer ' + self.token
            }
        )
        if response.status_code is 202 or response.status_code is 200:
            return json.loads(response.content)
        else:
            raise Exception(response.content)

    def downstream(self, url):
        """
        To make a GET request to Falkonry API server and return stream
        :param url: string
        """

        http = urllib3.PoolManager()
        response = http.request('GET', self.host + url, headers={'Authorization': 'Bearer '+self.token}, preload_content=False)
        if response.status is 200:
            return response
        else:
            raise Exception(response.content)
