import urllib.parse

from dsn_wechat import get_json

"""
关于OAuth2的一些方法，主要用于网页授权
"""

_WECHAT_URL_OAUTH = 'https://open.weixin.qq.com/connect/oauth2/authorize?' \
                    'appid=%(appid)s' \
                    '&%(redirect_uri)s' \
                    '&response_type=code' \
                    '&scope=%(scope)s&state=1#wechat_redirect'

_WECHAT_URL_TOKEN = 'https://api.weixin.qq.com/sns/oauth2/access_token?' \
                    'appid=%(appid)s' \
                    '&secret=%(secret)s' \
                    '&code=%(code)s' \
                    '&grant_type=authorization_code'

_WECHAT_URL_USERINFO = 'https://api.weixin.qq.com/sns/userinfo?' \
                       'access_token=%(token)s' \
                       '&openid=%(openid)s' \
                       '&lang=zh_CN'


def get_oauth2_url(app_id: str, redirect_uri: str, scope: str = 'snsapi_userinfo'):
    q = {'redirect_uri': redirect_uri}
    redirect = urllib.parse.urlencode(q, encoding='UTF-8')
    param = {'appid': app_id, 'redirect_uri': redirect, 'scope': scope}
    url = _WECHAT_URL_OAUTH % param
    return url


def get_access_token(app_id: str, secret: str, code: str):
    param = {'appid': app_id, 'secret': secret, 'code': code}
    url = _WECHAT_URL_TOKEN % param
    return get_json(url)


def get_user_info(token: str, openid: str):
    param = {'token': token, 'openid': openid}
    url = _WECHAT_URL_USERINFO % param
    return get_json(url)
