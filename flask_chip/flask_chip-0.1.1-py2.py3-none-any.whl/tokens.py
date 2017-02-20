# -*- coding: utf-8 -*-

from typing import Any  # noqa

from itsdangerous import SignatureExpired, BadSignature, TimedJSONWebSignatureSerializer as Serializer


def generate(data, key, expiration=24 * 60 * 60):
    # type: (Any, str, int) -> str
    s = Serializer(key, expires_in=expiration)
    token = s.dumps(data)
    return token.decode('utf-8')


def verify(token, key):
    # type: (str, str) -> Any
    s = Serializer(key)
    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature, TypeError):
        return None

    return data
