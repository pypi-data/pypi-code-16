# -*- coding: utf-8 -*-

from takumi_http.utils import Headers, Qs, HttpMeta


def test_headers():
    meta = {}
    headers = Headers(meta)
    headers['content-length'] = '45'
    assert headers['Content-Length'] == '45'
    assert list(headers.items()) == [('content-length', '45')]
    assert list(headers.keys()) == ['content-length']
    assert list(headers.values()) == ['45']
    assert headers.get('content-Length') == '45'
    assert headers.get('content-type', 'text/html') == 'text/html'
    assert 'Content-Length' in headers
    assert 'Content-Type' not in headers
    assert meta == {'__HEADER__content-length': '45'}


def test_qs():
    meta = {}
    qs = Qs(meta)
    qs['hello'] = '123'
    assert qs['hello'] == '123'
    assert list(qs.items()) == [('hello', '123')]
    assert list(qs.keys()) == ['hello']
    assert list(qs.values()) == ['123']
    assert 'hello' in qs
    assert 'world' not in qs
    assert meta == {'__QUERY_STRING__hello': '123'}


def test_http_meta():
    ctx = {
        'method': 'POST',
        'http_version': 'http/1.1',
        '__HEADER__content-length': '345',
        '__QUERY_STRING__hello': '123',
    }
    meta = HttpMeta(ctx)
    assert meta.method == 'POST'
    assert meta.http_version == 'http/1.1'
    assert meta.headers['content-length'] == '345'
    assert meta.qs['hello'] == '123'
