import json
from urllib import urlencode, quote

import requests
from cached_property import cached_property
from requests import HTTPError

from configuration import Configuration
from request import add_transunion_info
from response import raise_for_api_errors
from transunion.errors import InvalidCredentials
from transunion.utils import xml


class TransUnionClient(object):
    def __init__(self, username, password, industry_code, member_code,
                 prefix_code, sub_password, prod=False):
        self.config = Configuration(username, password, industry_code,
                                    member_code, prefix_code, sub_password,
                                    prod)

    def get_response(self, application_info):
        payload = self._get_payload(application_info)
        res = self._request(payload)
        self._validate_response(res)
        return TransUnionResponse(res)

    def _request(self, payload):
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
        }
        res = requests.request(method="POST", url=self.config.api_url,
                               data=payload, headers=headers)
        return res

    def _get_payload(self, applicant_info):
        payload_dict = add_transunion_info(self.config, applicant_info)
        applicant_info = quote(xml.dumps(payload_dict), safe='')
        query = {
            'username': self.config.username,
            'password': self.config.password,
            'type': 'PFS',
        }
        payload = urlencode(query) + '&PFS={}'.format(applicant_info)
        return payload

    def _validate_response(self, res):
        try:
            res.raise_for_status()
        except HTTPError as e:
            if res.status_code == 401:
                raise InvalidCredentials(self.config.api_url)
            else:
                raise e


class TransUnionResponse(object):
    def __init__(self, response):
        self.response = response

    @cached_property
    def xml(self):
        """
        return xml string
        """
        return self.response.content

    @cached_property
    def data(self):
        """
        return dictionary
        """
        data = xml.loads(self.xml)
        raise_for_api_errors(data)
        return data

    @cached_property
    def json(self):
        """
        return json string
        """
        return json.dumps(self.data)
