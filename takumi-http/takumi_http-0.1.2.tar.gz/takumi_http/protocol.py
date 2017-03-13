# -*- coding: utf-8 -*-

"""
takumi_http.protocol
~~~~~~~~~~~~~~~~~~~~

Http <=> Thrift

http:

GET /ping HTTP/1.1
Host: localhost
Connection: keep-alive
Content-Length: 13602
Pragma: no-cache
Cache-Control: no-cache
Origin: https://github.com
User-Agent: Mozilla/5.0
content-type: application/json

{
  "hello": 124
}


=>

meta:
{
  "method": "GET",
  "http_version": "HTTP/1.1",
  "user-agent": "Mozilla/5.0",
  ...
}
"""
import logging
import contextlib
from thriftpy.thrift import TMessageType, TApplicationException, \
    TDecodeException
from takumi import CloseConnectionError
from takumi_thrift import Metadata
from takumi_thrift.wrappers import META_API_NAME

from .http_handler import HttpHandler, HttpRequest
from ._json import struct_from_json, struct_to_json


logger = logging.getLogger('takumi.http')


class HTTPError(object):
    """Represents a http error
    """
    def __init__(self, code, message=''):
        self.code = code
        self.message = message

    def to_dict(self):
        return {'code': self.code, 'message': self.message}


@contextlib.contextmanager
def _decode_exception(http):
    try:
        yield
    except TDecodeException as e:
        logger.exception(e)
        http.write_response({'status_code': 500}, {'message': str(e)})
        raise CloseConnectionError


class THttpProtocol(object):
    """Http protocol adapted for thrift

    :param trans: client socket
    """
    def __init__(self, trans):
        self.trans = trans
        self.http = HttpHandler(trans.sock, None, None)
        self._is_meta_read = False
        self._write_exception = False
        self._written_meta = None
        self._req = None

    def skip(self, ttype):
        pass

    def read_message_begin(self):
        if self._req is None:
            self._req = self.http.get_request()
            if not isinstance(self._req, HttpRequest):
                self.http.write_response(self._req.meta, self._req.body)
                raise CloseConnectionError

        api = self._req.api if self._is_meta_read else META_API_NAME
        return api, TMessageType.CALL, 0

    def read_message_end(self):
        if not self._is_meta_read:
            self._is_meta_read = True
        else:
            self._is_meta_read = False
            self._req = None

    def write_message_begin(self, name, ttype, seqid):
        if ttype == TMessageType.EXCEPTION:
            self._write_exception = True

    def write_message_end(self):
        pass

    def read_struct(self, obj):
        assert self._req is not None

        data = self._req.body or {} if \
            self._is_meta_read else {'data': self._req.meta}

        # Close connection when exception happened
        with _decode_exception(self.http):
            struct_from_json(data, obj)

    def _write_response(self, obj):
        if hasattr(obj, 'success') and isinstance(obj.success, HTTPError):
            data = obj.success.to_dict()
        else:
            # Close connection when exception happened
            with _decode_exception(self.http):
                data = struct_to_json(obj)

        meta = self._written_meta or {}
        if 'success' not in data:
            meta.setdefault('status_code', 500)

        # Extract suitable value
        values = list(data.values())
        if len(values) == 1:
            data = values[0]

        try:
            self.http.write_response(meta, data)
            if self.http.close_connection:
                raise CloseConnectionError
        finally:
            self._written_meta = None

    def write_struct(self, obj):
        if self._write_exception:
            self._write_exception = False
            self._written_meta = {'status_code': 500}
            if isinstance(obj, TApplicationException) and not obj.message:
                obj.message = str(obj)
            self._write_response(obj)
            return

        if isinstance(obj, Metadata):
            # write meta
            self._written_meta = obj.data
        else:
            self._write_response(obj)


class HttpProtocol(object):
    """Http protocol getter for takumi service runner

    :param sock: client socket
    """
    def __init__(self, sock):
        self.sock = sock

    def get_proto(self):
        """Create a THttpProtocol instance
        """
        return THttpProtocol(self.sock)

    def close(self):
        self.sock.close()
