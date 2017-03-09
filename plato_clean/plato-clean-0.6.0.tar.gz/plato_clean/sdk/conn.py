import json
import requests
from codes import codes
import errors


class Conn(object):
    def __init__(self, access_key, access_secret, endpoint, is_debug=False):
        self.access_key = access_key
        self.access_secret = access_secret
        self.endpoint = endpoint

    def make_headers(self):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Le-Key': self.access_key,
            'X-Le-Secret': self.access_secret,
        }
        return headers

    def call(self, action, payload={}):
        """
        make a action call.
        """
        url = self.endpoint
        headers = self.make_headers()

        payload['action'] = action
        res = requests.post(url, headers=headers, json=payload)

        data = self.parse_response(action, res)
        return data

    def parse_response(self, action, res):
        if res.status_code != 200:
            raise errors.HTTPError(res.status_code)

        ret = json.loads(res.text)
        ret_code = ret['retCode']
        data = ret['data']

        if ret_code == codes.ok:
            print action, 'ok'
            return data

        message = ret['message'] + '\n exceptionTag: ' + data['exceptionTag']

        if ret_code == codes.param_invalid:
            raise errors.ParamInvalidError(message)

        elif ret_code == codes.access_key_invalid:
            raise errors.AccessKeyInvalidError(message)

        elif ret_code == codes.resource_unauthorized:
            raise errors.ResourceUnauthorizedError(message)

        elif ret_code == codes.resource_not_found:
            raise errors.ResourceNotFoundError(message)

        elif ret_code == codes.action_disallow:
            raise errors.ActionDisallowError(message)

        elif ret_code == codes.request_format_invalid:
            raise errors.RequestFormatInvalidError(message)

        elif ret_code == codes.quota_not_enough:
            raise errors.QuotaNotEnoughError(message)

        elif ret_code == codes.server_error:
            raise errors.ServerErrorError(message)

        elif ret_code == codes.actions_totally_failed:
            raise errors.ActionsTotallyFailedError(message)

        elif ret_code == codes.actions_partially_failed:
            raise errors.ActionsPartiallyFailedError(message)

        else:
            raise Exception(message)
