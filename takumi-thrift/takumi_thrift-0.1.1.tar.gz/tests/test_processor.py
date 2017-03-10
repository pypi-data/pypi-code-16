# -*- coding: utf-8 -*-

import pytest
import mock
from takumi_thrift.processor import Processor
from takumi_thrift.wrappers import META_API_NAME, Response, Metadata
from thriftpy.thrift import TMessageType, TProcessor, TApplicationException


@pytest.fixture
def ctx():
    return type('ctx', (object,), {})


def test_process_in(proto, ctx):
    proto.read_message_begin = mock.Mock(
        return_value=(META_API_NAME, TMessageType.REPLY, 0))

    def mock_read_struct(obj):
        obj.data = {'hello': 'meta'}
    proto.read_struct = mock_read_struct

    processor = Processor(ctx, None, None)
    with mock.patch.object(TProcessor, 'process_in') as mock_process_in:
        processor.process_in(proto)
    mock_process_in.assert_called_with(proto)
    assert processor._ctx.meta == {'hello': 'meta'}
    assert processor._send_meta

    proto.read_message_begin = mock.Mock(
        return_value=('ping', TMessageType.REPLY, 0))
    with mock.patch.object(Processor, '_process_in') as mock__process_in:
        processor.process_in(proto)
    mock__process_in.assert_called_with(proto, 'ping', TMessageType.REPLY,
                                        0)


def test_send_result_not_support_meta(proto, ctx):
    res = mock.Mock()
    res.success = 123
    processor = Processor(ctx, None, None)
    with mock.patch.object(TProcessor, 'send_result') as mock_send_result:
        processor.send_result(proto, 'ping', res, 0)
    mock_send_result.assert_called_with(proto, 'ping', res, 0)
    proto.write_message_begin.assert_not_called()
    proto.write_struct.assert_not_called()
    proto.write_message_end.assert_not_called()


def test_send_result_without_meta(proto, ctx):
    res = mock.Mock()
    res.success = 123

    processor = Processor(ctx, None, None)
    processor._send_meta = True
    with mock.patch.object(TProcessor, 'send_result') as mock_send_result:
        processor.send_result(proto, 'ping', res, 0)
    mock_send_result.assert_called_with(proto, 'ping', res, 0)
    proto.write_message_begin.assert_not_called()
    proto.write_struct.assert_not_called()
    proto.write_message_end.assert_not_called()


def test_send_result_with_meta(proto, ctx):
    res = mock.Mock()
    res.success = Response(value=123, meta={'hello': 'meta'})

    processor = Processor(ctx, None, None)
    processor._send_meta = True
    with mock.patch.object(TProcessor, 'send_result') as mock_send_result:
        processor.send_result(proto, 'ping', res, 0)
    mock_send_result.assert_called_with(proto, 'ping', res, 0)
    assert res.success == 123
    proto.write_struct.assert_called_with(Metadata({'hello': 'meta'}))


def test_do_process(proto, ctx):
    processor = Processor(ctx, None, None)
    processor.send_exception = mock.Mock()
    ret = TApplicationException(0)
    with mock.patch.object(
            Processor, 'process_in',
            return_value=(
                'ping', 0, ret, None)) as mock_process_in:
        processor._process(proto, proto)
    mock_process_in.assert_called_with(proto)
    processor.send_exception.assert_called_with(proto, 'ping', ret, 0)

    ret = TApplicationException(0, 'unknown error')

    def mock_call():
        raise ret

    with mock.patch.object(
            Processor, 'process_in', return_value=(
                'ping', 0, None, mock_call
            )) as mock_process_in:
        processor._process(proto, proto)
    mock_process_in.assert_called_with(proto)
    processor.send_exception.assert_called_with(proto, 'ping', ret, 0)


def test_process(proto, ctx):
    processor = Processor(ctx, None, None)
    processor._metadata = 'meta'

    with mock.patch.object(Processor, '_process') as mock_process:
        processor.process(proto, proto)
    mock_process.assert_called_with(proto, proto)
    assert processor._ctx.meta == {}


def test_do_process_in(proto, ctx):
    import takumi_thrift.processor as takumi_thrift_processor

    def t_app_exeception(code):
        return code
    vars(t_app_exeception).update(
        vars(takumi_thrift_processor.TApplicationException))

    processor = Processor(ctx, None, None)
    processor._service = mock.Mock()
    processor._service.thrift_services = []
    with mock.patch.object(takumi_thrift_processor,
                           'TApplicationException', t_app_exeception):
        res = processor._process_in(proto, 'ping', TMessageType.REPLY, 0)
        assert res == (
            'ping', 0,
            takumi_thrift_processor.TApplicationException.UNKNOWN_METHOD,
            None)

    processor._service.thrift_services = ['ping']
    processor._service.ping_args = lambda: mock.Mock(thrift_spec={})
    processor._service.ping_result = mock.Mock()
    processor._process_in(proto, 'ping', TMessageType.REPLY, 0)
    processor._service.ping_result.assert_called_with()
