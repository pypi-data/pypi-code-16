import json
import logging

import requests

_WECHAT_URL_BASE = 'https://api.weixin.qq.com/cgi-bin/'
_WECHAT_URL_ACCESS_TOKEN = _WECHAT_URL_BASE + 'token'


class WechatError(RuntimeError):
    def __init__(self, errcode, errmsg):
        self.errcode = errcode
        self.errmsg = errmsg


def _get_logger():
    return logging.getLogger('dsn.wechat')


def post_json(url: str, obj: dict) -> dict:
    data = json.dumps(obj, ensure_ascii=False).encode('UTF-8')
    resp = requests.post(url, data=data)
    return _parse_response(resp)


def get_json(url: str, params: dict = None) -> dict:
    resp = requests.get(url, params)
    return _parse_response(resp)


def _parse_response(resp) -> dict:
    if resp.status_code == 200:
        obj = resp.json()
        code = obj.get('errcode')
        if code and code != 0:
            raise WechatError(obj.get('errcode'), obj.get('errmsg'))
        return obj
    resp.raise_for_status()


def get_access_token(appid: str, secret: str) -> dict:
    params = {'grant_type': 'client_credential',
              'appid': appid,
              'secret': secret}
    rst = get_json(_WECHAT_URL_ACCESS_TOKEN, params)
    _get_logger().debug(json)
    return rst
