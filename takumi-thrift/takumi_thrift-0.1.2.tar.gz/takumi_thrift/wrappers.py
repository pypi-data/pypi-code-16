# -*- coding: utf-8 -*-

"""
takumi_thrift.wrappers
~~~~~~~~~~~~~~~~~~~~~~

Defines Response object for wrapping api result.
"""

from thriftpy.thrift import TMessageType, TPayload, TType

META_API_NAME = '__takumi_meta_api_v1__'
HEALTH_CHECK_API_NAME = '__takumi_ping__'


class Response(object):
    """Represents api result with arbitrary optinal metadata
    """
    def __init__(self, value, meta=None):
        self.value = value
        self.meta = meta or {}

    def __repr__(self):
        return '<Response {!r}>'.format(self.value)

    def __eq__(self, other):
        return self.value == other.value and self.meta == other.meta


class Metadata(TPayload):
    """Metadata passed between client and server
    """
    thrift_spec = {
        1: (TType.MAP, 'data', (TType.STRING, TType.STRING), False)
    }

    def __init__(self, meta=None):
        self.data = meta or {}

    def send(self, oprot, seqid):
        oprot.write_message_begin(META_API_NAME, TMessageType.REPLY, seqid)
        self.write(oprot)
        oprot.write_message_end()

    def recv(self, iprot):
        self.read(iprot)
        iprot.read_message_end()
