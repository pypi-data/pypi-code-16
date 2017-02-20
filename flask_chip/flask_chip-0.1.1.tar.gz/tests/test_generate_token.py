# -*- coding: utf-8 -*-

import pytest  # type: ignore
import six

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask_chip.tokens import generate


@pytest.fixture
def key():
    return 'secretkey'


def test_generated_token_is_string(key):
    data = {'foo': ['bar', 'baz']}
    token = generate(data, key)

    assert isinstance(token, six.string_types)


def test_generated_token_contains_usrer_id(key):
    data = {'foo': ['bar', 'baz']}
    token = generate(data, key)

    s = Serializer(key)
    result = s.loads(token)

    assert result == data
