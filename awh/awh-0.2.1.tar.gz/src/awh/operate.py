"""Collection of functions which should ease up operating on incoming data."""

import os
import hmac
import json
import collections
import contextlib
import tempfile
import shutil

import jsonpath_rw


JSONMatch = collections.namedtuple('JSONMatch', ['path', 'value'])


class ValidationFailure(Exception):
    """Base class used by default by require()"""
    pass


def require(bool_expr, msg="", exc=ValidationFailure):
    """Raises an exception of type exc if a given bool_expr evaluates to
    false. This is particulary useful when writing validators to avoid spaghetti
    if-else statements."""
    if not bool_expr:
        raise exc(msg)


@contextlib.contextmanager
def tempdir():
    """Context manager function (should be used by `with` statement) which
    creates and returns a temporary directory. When it goes out of scope,
    directory and all its contents is removed."""
    try:
        dir_ = tempfile.mkdtemp()
        yield dir_
    finally:
        shutil.rmtree(dir_)


@contextlib.contextmanager
def chdir(path):
    """Context manager function (should be used by `with` statement) which
    changes a current directory to a given `path`. When it goes out of scope,
    directory is changed back to the old one."""
    oldcwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(oldcwd)


def digest_eq(lhs, rhs):
    """Cryptographically appropriate check of equality of two
    objects/callables.

    See documentation for hmac.compare_digest for comparison details."""
    return hmac.compare_digest(lhs, rhs)


def jsonpath(json_in, path):
    """Returns a list of all JSONMatch objects which match a given jsonpath.
    JSONMatch contains full path to the value and a value itself:

        class JSONMatch:
            JSONMatch(path, value)

    JSONPath is a language which can be used for quick extraction of data from
    JSON objects. It's similar to XPath known to extract data from XMLs.

    awh uses jsonpath-rw implementation of jsonpath. You can learn about
    supported syntax on library's webpage:
    <https://github.com/kennknowles/python-jsonpath-rw>"""
    expr = jsonpath_rw.parse(path)
    return [JSONMatch(path=str(m.full_path), value=m.value)
            for m in expr.find(json_in)]


def jsonpath_s(json_str, path):
    """Convienience function which accepts unparsed json string, parses it and
    calls jsonpath.

    For usage, see @jsonpath description."""
    return jsonpath(json.loads(json_str), path)
