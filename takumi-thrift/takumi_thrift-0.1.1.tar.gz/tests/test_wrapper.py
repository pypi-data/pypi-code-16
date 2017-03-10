# -*- coding: utf-8 -*-

from takumi_thrift.wrappers import Metadata, META_API_NAME, Response


def test_meta_send(proto):
    meta = Metadata({'hello': 'meta'})
    meta.send(proto, 0)
    proto.write_message_begin.assert_called_with(META_API_NAME, 2, 0)
    proto.write_struct.assert_called_with(meta)
    proto.write_message_end.assert_called_with()


def test_meta_recv(proto):
    meta = Metadata({'hello': 'meta'})
    meta.recv(proto)
    proto.read_struct.assert_called_with(Metadata({'hello': 'meta'}))
    proto.read_message_end.assert_called_with()


def test_response():
    res = Response(123, meta={'hello': 'meta'})
    assert res.value == 123
    assert res.meta == {'hello': 'meta'}
