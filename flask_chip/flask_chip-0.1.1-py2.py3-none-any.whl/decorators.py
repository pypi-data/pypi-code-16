# -*- coding: utf-8 -*-
from functools import wraps, partial

from flask import request, current_app as app
from toolz import pipe

from .utils import save_user, unauthorized
from .tokens import verify as verify_token


def verify(f, pipeline, on_none):
    '''Run given pipeline, when result is not None run decorated function
    otherwise run on_none function

    :param f: guarded function
    :param pipline: token proccesing pipeline
    :param on_none: function called when pipeline result is None
    :returns: function
    '''
    @wraps(f)
    def _verify(*args, **kwargs):
        result = pipe(*pipeline)
        return f(*args, **kwargs) if result is not None else on_none()

    return _verify


def create_verify_user(get_user, header_key='X-Auth-Token', on_none=unauthorized):
    '''Create user verify decorator.

    :param get_user: function that returns user object based on data from the token
    :param header_key: token header field name
    :param on_none: function called when pipeline result is None
    :returns: user verify decorator
    '''
    pipeline = (
        header_key,
        lambda key: request.headers.get(key, ''),
        lambda token: verify_token(token, app.config['SECRET_KEY']),
        get_user,
        save_user,
    )

    return partial(verify, pipeline=pipeline, on_none=on_none)


def create_verify_single_use_token(exists_and_remove, header_key='X-Single-Use-Token', on_none=unauthorized):
    '''Create one-time-access token verify decorator

    :param exists_and_remove: function that return key when exists in store and remove it
    :param header_key: token header field name
    :param on_none: function called when pipeline result is None
    :returns: token exists decorator
    '''
    pipeline = (
        header_key,
        lambda key: request.headers.get(key, ''),
        exists_and_remove,
        lambda token: verify_token(token, app.config['SECRET_KEY']),
    )

    return partial(verify, pipeline=pipeline, on_none=on_none)
