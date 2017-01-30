#!/usr/bin/env python3

import re
from functools import wraps

from flask import abort, request

TOKENS = []
REGEX_USERNAME = re.compile('^\w{1,20}$')


def authorize_badtoken(f):
    @wraps(f)
    def check_token(*args, **kwargs):
        magic_header = request.environ.get('HTTP_BADTOKEN')
        if magic_header in TOKENS:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return check_token


def sanitize_user():
    def decorator(f):
        @wraps(f)
        def check_user(*args, **kwargs):
            if REGEX_USERNAME.match(kwargs.get('user')):
                return f(*args, **kwargs)
            else:
                return abort(400)
        return check_user
    return decorator
