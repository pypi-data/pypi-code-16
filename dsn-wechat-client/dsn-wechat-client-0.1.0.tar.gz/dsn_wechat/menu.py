from dsn_wechat import _WECHAT_URL_BASE
from dsn_wechat import post_json

"""
微信公众号菜单管理
"""

_WECHAT_URL_MENU_CREATE = _WECHAT_URL_BASE + 'menu/create?access_token=%s'


def create(token: str, menu: dict):
    assert token, '[access_token] is None'
    url = _WECHAT_URL_MENU_CREATE % token
    return post_json(url, menu)
