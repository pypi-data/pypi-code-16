"""Dry run webhooks by passing them raw HTTP requests similar (or same) as ones
sent by real web services.

This module is installed along with awh library as `awh-validate` script."""

# pylint: disable=protected-access

import os
import sys
import site
import argparse
import contextlib
import http.server
import importlib
import traceback
import textwrap

from werkzeug.test import Client, EnvironBuilder
from werkzeug.datastructures import Headers


class HTTPRequest(http.server.BaseHTTPRequestHandler):
    """HTTP parser, thanks to Brandon Rhodes, with some modifications for
    Python 3 and reading from file: http://stackoverflow.com/a/5955949/1088577

    Constructor accepts a file-like binary object - it's required by http.server
    for Python 3, because it tries to decode requestline.
    """
    class ParseError(Exception):
        """Exception raised when an error occures during parsing HTTP
        request."""
        def __init__(self, ec, em):
            super().__init__(ec, em)

        @property
        def code(self):
            """Error code of parsing error."""
            return self.args[0]

        @property
        def message(self):
            """Textual description of parsing error."""
            return self.args[1]

    def __init__(self, binary_file):
        # pylint: disable=super-init-not-called
        self.rfile = binary_file
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()
        if self.error_code:
            raise HTTPRequest.ParseError(self.error_code, self.error_message)

        # file position  pointer is at the right place after parsing headers
        # (which parse_request only does). It's payload time!
        payload = self.rfile.read()
        self.headers.set_payload(payload)
        self.headers['Content-Length'] = len(payload)

        # make headers wsgi-like
        bigh = []
        for key, val in self.headers.items():
            newkey = "HTTP_%s" % key.replace('-', '_').upper()
            bigh.append((newkey, val))

        # There's no clear() for headers :(
        for key in self.headers.keys():
            del self.headers[key]

        for key, val in bigh:
            self.headers[key] = val

    def send_error(self, code, message, **kwargs):
        # pylint: disable=unused-argument
        self.error_code = code
        self.error_message = message


class _FuncWrapper:
    def __init__(self, func, call=True):
        self._func = func
        self._call = call

        self.call_count = 0
        self.returned = None
        self.args = []
        self.kwargs = []
        self.tb = []

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        try:
            self.args.append(tuple(args))
            self.kwargs.append({k: v for k, v in kwargs.items()})
            if self._call is False:
                self.returned = '(call suppressed)'
                return
            self.returned = self._func(*args, **kwargs)
            return self.returned
        except Exception:
            self.tb.append(traceback.format_exc())
            raise
        else:
            self.tb.append(None)

    def __str__(self):
        info = 'call count: %d\n' % self.call_count
        info += 'arguments: %s\n' % self.args
        info += 'keyword arguments: %s\n' % self.kwargs
        info += 'return value: %s\n' % self.returned
        if any(tb for tb in self.tb):
            info += 'exceptions for each call:\n'
            for tb in self.tb:
                info += '\n'
                if tb:
                    info += tb
                else:
                    info += '(no exception)\n'
        return info


def _eprint(*args, **kwargs):
    """Prints something to stderr"""
    print(*args, file=sys.stderr, **kwargs)


def _die(errno, *args, **kwargs):
    """Prints something to stderr and exits program with errno"""
    _eprint(*args, **kwargs)
    sys.exit(errno)


def _import_app(spec):
    """Imports app from spec in form 'module:app'"""
    mod_name, sep, app_name = spec.strip().partition(':')
    if not (mod_name and sep and app_name):
        _die(1, 'Incorrect application specification: "%s"' % spec)

    mod = importlib.import_module(mod_name)
    return getattr(mod, app_name)


def _make_env_builder(http_req):
    headers = Headers(http_req.headers.items())
    req_headers = http_req.headers
    return EnvironBuilder(method=http_req.command, headers=headers,
                          data=req_headers.get_payload(),
                          content_length=req_headers['HTTP_CONTENT_LENGTH'])


def _test(app, builder):
    for name, reg in app._registry.items():
        if reg.executor is not None:
            # disable calling executor
            reg.executor = _FuncWrapper(reg.executor, call=False)
        if reg.validator is not None:
            reg.validator = _FuncWrapper(reg.validator)

    c = Client(app)
    resp = c.open(builder)

    for name, reg in app._registry.items():
        print('%s:' % name)
        print('  validator:')
        print(textwrap.indent(str(reg.validator), '    '))
        print('  executor:')
        print(textwrap.indent(str(reg.executor), '    '))

    print('Response:')
    print('    %s' % str(resp))


def _parse_args():
    """Parses commandline options"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='infile',
                        help='input file. By default input is read from stdin')
    parser.add_argument('application', type=str,
                        help='application location in form of module:object')

    args = parser.parse_args()
    return args


@contextlib.contextmanager
def _read_input(infile):
    """Reads input either from file or stdin."""
    if infile is None:
        yield sys.stdin.buffer
    else:
        try:
            f = open(infile, 'rb')
        except FileNotFoundError:
            _die(1, "File not found: %s" % infile)

        try:
            yield f
        finally:
            f.close()


def main():
    args = _parse_args()

    # allows writing application spec relative to PWD
    site.addsitedir(os.getcwd())

    try:
        with _read_input(args.infile) as f:
            raw_req = HTTPRequest(f)
    except HTTPRequest.ParseError as e:
        _die(1, e.message)

    app = _import_app(args.application)
    builder = _make_env_builder(raw_req)

    _test(app, builder)
    return 0
