# -*- coding: utf-8 -*-

"""
takumi_thrift.client
~~~~~~~~~~~~~~~~~~~~

This module implements a Thriftpy client which can be used to pass
metadata.
"""

from thriftpy.thrift import TClient, TMessageType, TApplicationException
from .wrappers import Metadata, META_API_NAME, Response


class Client(TClient):
    """Sending and receiving metadata

    .. note::

        This class is not thread safe.
    """
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self._metadata = None
        self._support_meta = True

    # Copied from thriftpy.thrift.TClient._recv
    def _do_recv(self, _api, mtype):
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(self._iprot)
            self._iprot.read_message_end()
            raise x
        result = getattr(self._service, _api + "_result")()
        result.read(self._iprot)
        self._iprot.read_message_end()

        if hasattr(result, "success") and result.success is not None:
            return result.success

        # void api without throws
        if len(result.thrift_spec) == 0:
            return

        # check throws
        for k, v in result.__dict__.items():
            if k != "success" and v:
                raise v

        # no throws & not void api
        if hasattr(result, "success"):
            raise TApplicationException(TApplicationException.MISSING_RESULT)

    def _send(self, _api, **kwargs):
        if self._support_meta:
            meta = Metadata(kwargs.pop('meta', {}))
            meta.send(self._iprot, self._seqid)
        super(Client, self)._send(_api, **kwargs)

    def _recv(self, _api):
        fname, mtype, seqid = self._iprot.read_message_begin()
        if self._support_meta and fname == META_API_NAME:
            meta = Metadata()
            meta.recv(self._iprot)
            if mtype == TMessageType.EXCEPTION:
                self._support_meta = False
            elif mtype == TMessageType.REPLY:
                self._metadata = meta
            return super(Client, self)._recv(_api)
        return self._do_recv(_api, mtype)

    def _req(self, _api, *args, **kwargs):
        try:
            ret = super(Client, self)._req(_api, *args, **kwargs)
            meta = self._metadata.data if self._metadata else {}
            return Response(value=ret, meta=meta)
        finally:
            self._metadata = None
