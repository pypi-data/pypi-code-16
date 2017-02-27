#coding=utf-8

import hashlib
import hmac
import base64
from . import helper

ACCEPT = "Accept"
CONTENT_MD5 = "Content-MD5"
CONTENT_TYPE = "Content-Type"
DATE = "Date"
QUERY_SEPARATOR = "&"
HEADER_SEPARATOR = "\n"


def refresh_sign_headers(headers):
    """
    重新封装待签名的headers
    :param headers:
    :return:
    """
    if headers is None or not isinstance(headers, dict):
        headers = dict()
    if not headers.has_key('Date'):
        headers["Date"] = helper.get_rfc_2616_date()
    return headers


def compose_string_to_sign(method, query_params, body_params, headers=None):
    """
    封装待签名的字符串
    :param method:
    :param query_params:
    :param body_params:
    :param headers:
    :return:
    """
    sign_to_string = ""
    sign_to_string += method
    sign_to_string += HEADER_SEPARATOR
    # if headers.has_key(DATE) and headers[DATE] is not None:
    #     sign_to_string += headers[DATE]
    sign_to_string += HEADER_SEPARATOR
    sorted_map_query = sorted(query_params.items())
    for k,v in sorted_map_query:
        sign_to_string += k
        if v:
            sign_to_string += '='
            sign_to_string += str(v)
        sign_to_string += QUERY_SEPARATOR
    sorted_map_body = sorted(body_params.items())
    for k, v in sorted_map_body:
        sign_to_string += k
        if v:
            sign_to_string += '='
            sign_to_string += str(v)
        sign_to_string += QUERY_SEPARATOR
    if sign_to_string.endswith(QUERY_SEPARATOR):
        sign_to_string = sign_to_string[0: len(sign_to_string)-1]
    return sign_to_string


def get_signature(query_params, body_params, app_key, headers, method):
    """
    获得签名字符串
    :param query_params:
    :param app_key:
    :param headers:
    :param method:
    :return:
    """
    headers = refresh_sign_headers(headers=headers)
    sign_to_string = compose_string_to_sign(
        method=method,
        query_params=query_params,
        body_params=body_params,
        headers=headers)
    h = hmac.new(app_key, sign_to_string, hashlib.sha1)
    signature = base64.encodestring(h.digest()).strip()
    return signature


def get_signature_headers(query_params, body_params, app_id, app_key, headers, method):
    signature = get_signature(query_params, body_params, app_key, headers, method)
    headers["Authorization"] = "wxs "+app_id+":"+signature
    return headers
