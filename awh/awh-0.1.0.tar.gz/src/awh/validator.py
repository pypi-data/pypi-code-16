"""Dry run webhooks by passing them raw HTTP requests similar (or same) as ones
sent by real web services.

This module is installed along with awh library as `awh-validate` script."""

# pylint: disable=protected-access

import os
import sys
import site
import copy
import argparse
import contextlib
import http.server
import importlib

from werkzeug.test import Client, EnvironBuilder
from werkzeug.wrappers import Request, Response
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


def _test_validators(app, builder):
    validators = [reg.validator
                  for _, reg in app._registry.items() if reg.validator]
    print('%d registered validators' % len(validators))

    req = Request(builder.get_environ())
    for name, reg in app._registry.items():
        if not reg.validator:
            continue

        try:
            result = reg.validator(req)
        except Exception as e:
            print('    %s: %s(request) -> raises %s' %
                  (name, reg.validator._func.__name__, type(e).__name__))
            print("        MESSAGE: %s" % e)
        else:
            print('    %s: %s(request) -> %s' %
                  (name, reg.validator._func.__name__, str(result)))


def _test_executors(app):
    executors = [reg.executor
                 for _, reg in app._registry.items() if reg.executor]
    print('%d registered executors' % len(executors))

    for name, reg in app._registry.items():
        if not reg.executor:
            continue
        print('    %s: %s' % (name, reg.executor._func.__name__))


def _test_response(app, builder):
    app_copy = copy.deepcopy(app)
    app_copy.clear()

    print('Application response:')
    if app_copy._resp_manipulator is not None:
        req = Request(builder.get_environ())
        resp = Response()
        try:
            app_copy._resp_manipulator(req, resp)
        except Exception as e:
            print('    %s(request, response) -> raises %s' %
                  (app_copy._resp_manipulator.__name__, type(e).__name__))
            print("        MESSAGE: %s" % e)
        else:
            print('    %s(request, response)' %
                  (app_copy._resp_manipulator.__name__))

    c = Client(app_copy)
    resp = c.open(builder)
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

    _test_validators(app, builder)
    _test_executors(app)
    _test_response(app, builder)
    return 0
