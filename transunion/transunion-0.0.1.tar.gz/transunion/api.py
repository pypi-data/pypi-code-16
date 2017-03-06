from urllib import urlencode, quote

import requests

from configuration import Configuration
from request import add_transunion_info
from response import raise_for_api_errors, get_report
from transunion.utils.xml_convert import loads, dumps


class TransUnionClient(object):
    def __init__(self, username, password, industry_code, member_code,
                 prefix_code, sub_password, prod=False):
        self.config = Configuration(username, password, industry_code,
                                    member_code, prefix_code, sub_password,
                                    prod)

    def get_credit_report(self, application_info):
        payload = self._get_payload(application_info)
        response = self._request(payload)
        report = self._process_response(response)
        return report

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
        applicant_info = quote(dumps(payload_dict), safe='')
        query = {
            'username': self.config.username,
            'password': self.config.password,
            'type': 'PFS',
        }
        payload = urlencode(query) + '&PFS={}'.format(applicant_info)
        return payload

    def _process_response(self, res):
        res.raise_for_status()
        data = loads(res.content)
        raise_for_api_errors(data)
        report = get_report(data)
        return report
