# -*- coding: utf-8 -*-

"""
takumi_thrift.processor
~~~~~~~~~~~~~~~~~~~~~~~

This module implements an enhanced TProcessor for passing metadata.
"""

from thriftpy.thrift import TProcessor, TType, TApplicationException
from .wrappers import Response, Metadata, META_API_NAME


class Processor(TProcessor):
    """Implements Metadata passing

    .. note::

        This class is not thread safe.
    """
    def __init__(self, ctx, *args, **kwargs):
        super(Processor, self).__init__(*args, **kwargs)
        self._send_meta = False
        self._ctx = ctx
        self._ctx.meta = {}

    # Copied from TProcessor.process_in
    def _process_in(self, iprot, api, tp, seqid):
        if api not in self._service.thrift_services:
            iprot.skip(TType.STRUCT)
            iprot.read_message_end()
            result = TApplicationException(
                TApplicationException.UNKNOWN_METHOD)
            return api, seqid, result, None

        args = getattr(self._service, api + "_args")()
        args.read(iprot)
        iprot.read_message_end()
        result = getattr(self._service, api + "_result")()

        # convert kwargs to args
        api_args = [args.thrift_spec[k][1] for k in sorted(args.thrift_spec)]

        def call():
            f = getattr(self._handler, api)
            return f(*(args.__dict__[k] for k in api_args))

        return api, seqid, result, call

    def process_in(self, iprot):
        api, tp, seqid = iprot.read_message_begin()
        if api == META_API_NAME:
            # Receive meta
            meta = Metadata()
            meta.recv(iprot)
            self._send_meta = True
            self._ctx.meta = meta.data
            return super(Processor, self).process_in(iprot)
        return self._process_in(iprot, api, tp, seqid)

    def send_result(self, oprot, api, result, seqid):
        if hasattr(result, 'success'):
            call_value = result.success
            if isinstance(call_value, Response):
                meta = Metadata(call_value.meta)
                result.success = call_value.value

                # Send meta
                if self._send_meta:
                    try:
                        meta.send(oprot, seqid)
                    finally:
                        self._send_meta = False

        return super(Processor, self).send_result(oprot, api, result, seqid)

    def _process(self, iprot, oprot):
        api, seqid, result, call = self.process_in(iprot)
        if isinstance(result, TApplicationException):
            return self.send_exception(oprot, api, result, seqid)

        try:
            result.success = call()
        except TApplicationException as e:
            # Send unexpected application exception
            return self.send_exception(oprot, api, e, seqid)
        except Exception as e:
            # raise if api don't have throws
            self.handle_exception(e, result)

        if not result.oneway:
            self.send_result(oprot, api, result, seqid)

    def process(self, iprot, oprot):
        try:
            self._process(iprot, oprot)
        finally:
            self._ctx.meta = {}
