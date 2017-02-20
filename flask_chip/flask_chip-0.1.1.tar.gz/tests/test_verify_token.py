# -*- coding: utf-8 -*-

import pytest  # type: ignore
import time

from flask_chip.tokens import generate, verify


@pytest.fixture
def key():
    return 'secretkey'


@pytest.fixture
def data():
    return {'foo': ['bar', 'baz']}


@pytest.fixture
def token(data, key):
    return generate(data, key)


@pytest.fixture
def expired_token(data, key):
    return generate(data, key, 0)


def test_return_stored_data_when_token_is_right(data, key, token):
    result = verify(token, key)

    assert result is not None
    assert result == data


def test_return_none_when_token_expire(data, key, expired_token):
    time.sleep(1)

    result = verify(expired_token, key)

    assert result is None


def test_return_none_when_token_is_wrong(data, key):
    result = verify('', key)

    assert result is None
