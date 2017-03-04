# -*- coding: utf-8 -*-

import pytest
import mock
from thriftpy.thrift import TMessageType, TPayload, TType, \
    TApplicationException
from thriftpy.transport import TSocket
from takumi_http.protocol import THttpProtocol, CloseConnectionError
from takumi_http.http_handler import HttpRequest, HttpError
from takumi_thrift.wrappers import META_API_NAME, Metadata


class Obj(TPayload):
    thrift_spec = {1: (TType.I32, 'hello', True)}


@pytest.fixture
def proto():
    sock = TSocket(host='localhost', port=1999)
    sock._init_sock()
    return THttpProtocol(sock)


def test_read_message_begin(proto, monkeypatch):
    proto.http.write_response = mock.Mock()
    proto.http.get_request = mock.Mock(return_value=HttpError(500, '', ''))
    with pytest.raises(CloseConnectionError):
        proto.read_message_begin()
    proto.http.write_response.assert_called_with({
        'content-type': 'application/json;charset=utf-8',
        'connection': 'close',
        'status_code': '500',
        'message': '',
        'content-length': '15'
    }, {'message': ''})
    proto.http.get_request.assert_called_with()

    proto._req = None
    req = HttpRequest()
    req.api = 'ping'
    proto.http.get_request = mock.Mock(return_value=req)
    assert proto.read_message_begin() == (META_API_NAME, 1, 0)


def test_read_message_end(proto):
    proto._is_meta_read = True
    proto._req = HttpRequest()
    proto.read_message_end()
    assert not proto._is_meta_read
    assert proto._req is None

    proto.read_message_end()
    assert proto._is_meta_read


def test_write_message_begin(proto):
    assert not proto._write_exception
    proto.write_message_begin('ping', TMessageType.REPLY, 0)
    assert not proto._write_exception
    proto.write_message_begin('ping', TMessageType.EXCEPTION, 0)
    assert proto._write_exception


def test_read_struct(proto):
    proto._req = HttpRequest()
    proto._req.body = {'hello': 123}
    proto._req.method = 'POST'
    proto._req.http_version = 'http/1.1'
    obj = Metadata()
    proto.read_struct(obj)
    assert obj.data == {'method': 'POST', 'http_version': 'http/1.1'}

    proto.read_message_end()
    obj = Obj()
    proto.read_struct(obj)
    assert obj.hello == 123


def test_write_struct(proto):
    obj = Metadata()
    obj.data = {'status_code': 201}
    proto.write_struct(obj)
    assert proto._written_meta == {'status_code': 201}
    obj = Obj()
    obj.hello = 123

    proto.http.write_response = mock.Mock()
    proto.http.close_connection = 0
    proto.write_struct(obj)
    proto.http.write_response.assert_called_with(
        {'status_code': 201}, 123)
    assert proto._written_meta is None

    proto._write_exception = True
    proto.http.write_response = mock.Mock()
    obj = TApplicationException(TApplicationException.UNKNOWN_METHOD)
    proto.write_struct(obj)
    proto.http.write_response.assert_called_with(
        {'status_code': 500}, {'type': 1, 'message': 'Unknown method'})


def test_http_protocol():
    from takumi_http.protocol import HttpProtocol
    sock = TSocket(host='localhost', port=1998)
    sock._init_sock()
    factory = HttpProtocol(sock)
    factory.get_proto()
    factory.close()
