# -*- coding: utf-8 -*-

import mock
import json
import socket
import pytest

from takumi_service.exc import CloseConnectionError
from takumi_http.http_handler import HttpRequest


@pytest.fixture
def mock_sock():
    return socket.socket()


@pytest.fixture
def handle():
    from takumi_http.http_handler import HttpHandler
    sock = socket.socket()
    return HttpHandler(sock, None, None)


def test_http_error():
    from takumi_http.http_handler import HttpError
    ret = HttpError(400, 'Not Found', 'No such api')
    assert ret.meta == {
        'content-length': '26',
        'message': 'Not Found',
        'content-type': 'application/json;charset=utf-8',
        'status_code': '400',
        'connection': 'close'
    }

    assert ret.body == {'message': 'No such api'}


def test_http_request():
    ret = HttpRequest()
    ret.method = 'POST'
    ret.http_version = 'http/1.1'
    ret.headers = {'Content-Type': 'application/json'}
    ret.qs = {'hello': ['90']}
    ret.api = 'ping'

    assert ret.meta == {
        '__HEADER__content-type': 'application/json',
        'method': 'POST',
        'http_version': 'http/1.1',
        '__QUERY_STRING__hello': '90'
    }

    assert ret.body is None


def test_do_post(handle):
    data = {'hello': 123}
    handle.rfile = mock.Mock()
    handle.rfile.read = mock.Mock(
        return_value=json.dumps(data).encode('utf-8'))

    handle.headers = {}
    try:
        handle._request = HttpRequest()
        handle.do_POST()
        assert handle._request.body is None
        assert handle._error.code == 204
    finally:
        handle._request = None
        handle._error = None

    handle.headers = {'content-length': len(json.dumps(data))}
    try:
        handle._request = HttpRequest()
        handle.do_POST()
        assert handle._request.body == {'hello': 123}
    finally:
        handle._request = None

    handle.rfile.read = mock.Mock(return_value=b'\xff\xf4\xd8\x00\xdf')
    handle.do_POST()
    assert handle._error.code == 400


def test_send_error(handle):
    handle.send_error(400, explain='error happened')
    assert handle._error.code == 400
    assert handle._error.explain == 'error happened'
    assert handle._error.message == 'Bad Request'


def test_handle_one_request(handle):
    handle.rfile = mock.Mock()
    handle.rfile.readline = mock.Mock(return_value='')
    with pytest.raises(CloseConnectionError):
        handle.handle_one_request()

    handle.rfile.readline = mock.Mock(return_value='a' * 65537)
    handle.handle_one_request()
    assert handle._error.code == 414

    handle.rfile.readline = mock.Mock(return_value='GET / http/1.1')
    handle.parse_request = mock.Mock()
    handle.handle_one_request()
    handle.parse_request.assert_called_with()


def test_get_request(handle):
    def mock_handle_one_request():
        handle.command = 'GET'
        handle.request_version = 'http/1.1'
        handle.headers = {}
        handle.path = '/api/ping?offset=90&limit=10'

    handle.handle_one_request = mock_handle_one_request
    ret = handle.get_request()
    assert ret.body is None
    assert ret.meta == {
        '__QUERY_STRING__limit': '10',
        '__QUERY_STRING__offset': '90',
        'http_version': 'http/1.1',
        'method': 'GET'
    }


def test_write_response(handle, monkeypatch):
    handle.send_response = mock.Mock()
    handle.send_header = mock.Mock()
    handle.end_headers = mock.Mock()
    handle.wfile = mock.Mock()

    handle.write_response({'x-header': 'a header'}, {'hello': 123})
    handle.send_response.assert_called_with(200, 'OK')
    handle.send_header.assert_has_calls([
        mock.call('content-length', '14'),
        mock.call('content-type', 'application/json;charset=utf-8'),
        mock.call('x-header', 'a header'),
    ], any_order=True)
