import os
import sys
import io
from contextlib import contextmanager
from unittest import mock

import pytest

from markio.__main__ import main

DIRECTORY = os.path.join(os.path.dirname(__file__), 'examples')


class FakeExitError(RuntimeError):
    pass


def fake_exit(msg):
    if msg:
        raise FakeExitError(msg)


@contextmanager
def capture_print():
    F = io.StringIO()
    old_out = sys.stdout
    sys.stdout = F

    try:
        def value():
            return F.getvalue()

        yield value
    finally:
        sys.stdout = old_out


def test_markio_cmd_shows_source():
    path = os.path.join(DIRECTORY, 'valid-4.md')
    with capture_print() as value:
        with mock.patch('sys.exit', fake_exit):
            main(['src', path, '--lang', 'python'])

    assert value() == "print('hello world')\n"

    with capture_print() as value:
        with mock.patch('sys.exit', fake_exit):
            main(['src', path, '--lang', 'ruby'])

    assert value() == "puts 'hello world'\n"


def test_markio_cmd_shows_first_language():
    path = os.path.join(DIRECTORY, 'valid-4.md')
    with capture_print() as value:
        with mock.patch('sys.exit', fake_exit):
            main(['src', path])

    assert value() == "print('hello world')\n"


def _test_markio_cmd_shows_help():
    with capture_print() as value:
        with mock.patch('sys.exit', fake_exit):
            main(['-h'])

    assert value().startswith('usage: markio [-h]')

