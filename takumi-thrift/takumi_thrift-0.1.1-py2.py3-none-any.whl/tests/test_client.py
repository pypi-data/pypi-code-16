# -*- coding: utf-8 -*-

import mock
import pytest
from takumi_thrift.client import Client
from takumi_thrift.wrappers import Metadata, META_API_NAME, Response
from thriftpy.thrift import TMessageType, TApplicationException, TClient


def test_do_recv(proto):
    client = Client(None, None)
    client._iprot = proto
    client._service = mock.Mock()
    client._service.ping_result = mock.Mock()
    client._do_recv('ping', TMessageType.REPLY)

    with pytest.raises(TApplicationException) as exc_info:
        client._do_recv('ping', TMessageType.EXCEPTION)
    assert 'Default (unknown) TApplicationException' == str(exc_info.value)


def test_send(proto):
    client = Client(None, None)
    client._iprot = proto

    with mock.patch.object(TClient, '_send') as mock_send:
        client._send('ping', hello='world')
    mock_send.assert_called_with('ping', hello='world')
    proto.write_struct.assert_called_with(Metadata())


def test_send_not_support_meta(proto):
    client = Client(None, None)
    client._iprot = proto
    client._support_meta = False

    with mock.patch.object(TClient, '_send') as mock_send:
        client._send('ping', hello='world')
    mock_send.assert_called_with('ping', hello='world')
    proto.write_struct.assert_not_called()


def test_recv(proto):
    client = Client(None, None)
    client._iprot = proto

    proto.read_message_begin = mock.Mock(return_value=(
        'ping', TMessageType.REPLY, 0))
    with mock.patch.object(Client, '_do_recv') as mock_do_recv:
        client._recv('ping')
    mock_do_recv.assert_called_with('ping', 2)


def test_recv_meta(proto):
    client = Client(None, None)
    client._iprot = proto
    proto.read_message_begin = mock.Mock(return_value=(
        META_API_NAME, TMessageType.REPLY, 0))

    with mock.patch.object(TClient, '_recv') as mock_recv:
        client._recv('ping')
    mock_recv.assert_called_with('ping')
    assert client._metadata.data == {}
    proto.read_struct.assert_called_with(Metadata())


def test_recv_not_support_meta(proto):
    client = Client(None, None)
    client._iprot = proto
    proto.read_message_begin = mock.Mock(return_value=(
        META_API_NAME, TMessageType.EXCEPTION, 0))

    with mock.patch.object(TClient, '_recv') as mock_recv:
        client._recv('ping')
    mock_recv.assert_called_with('ping')
    assert client._metadata is None
    assert not client._support_meta


def test_req(proto):
    client = Client(None, None)
    client._iprot = proto

    with mock.patch.object(TClient, '_req', return_value=123) as mock_req:
        assert client._req('ping') == Response(123, meta={})
    mock_req.assert_called_with('ping')


def test_req_meta(proto):
    client = Client(None, None)
    client._iprot = proto
    client._metadata = Metadata({'hello': 'meta'})

    with mock.patch.object(TClient, '_req', return_value=123) as mock_req:
        assert client._req('ping') == Response(123, meta={'hello': 'meta'})
    mock_req.assert_called_with('ping')
    assert client._metadata is None
