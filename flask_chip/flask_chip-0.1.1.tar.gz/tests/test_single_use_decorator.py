# -*- coding: utf-8 -*-

import json
import pytest

from functools import partial

from flask.views import MethodView
from six.moves import http_client as http

from flask_chip.decorators import create_verify_single_use_token
from flask_chip.tokens import generate


tokens = set()


def pop(set_, key):
    try:
        set_.remove(key)
    except KeyError:
        return None

    return key


verify_ota = create_verify_single_use_token(partial(pop, tokens))


@pytest.fixture
def data():

    return ''


@pytest.fixture
def token(data, config):
    token = generate(data, config['SECRET_KEY'])
    tokens.add(token)
    return token


@pytest.fixture
def resource(app, data):

    class TestAPI(MethodView):
        @verify_ota
        def get(self):
            return 'Ok', http.OK

    app.add_url_rule('/test', view_func=TestAPI.as_view('test'))

    return app


def test_returns_status_ok(client, data, resource, token):
    rv = client.get(
        '/test',
        content_type='application/json',
        headers={
            'X-Single-Use-Token': token,
        }
    )

    response_data = rv.get_data(as_text=True)

    assert rv.status_code == http.OK
    assert response_data == 'Ok'


def test_returns_unauthorized(client, resource):
    rv = client.get(
        '/test',
        content_type='application/json',
        headers={
            'X-Single-Use-Token': token,
        }
    )

    response_data = json.loads(rv.get_data(as_text=True))

    assert rv.status_code == http.UNAUTHORIZED
    assert response_data['message'] == 'Unauthorized'
    assert response_data['status'] == http.UNAUTHORIZED
