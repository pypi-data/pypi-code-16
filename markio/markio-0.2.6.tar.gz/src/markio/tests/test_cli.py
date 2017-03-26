import io
import os
from contextlib import contextmanager
from unittest import mock

import sys

from markio.__main__ import main

DIRECTORY = os.path.join(os.path.dirname(__file__), 'examples')


class FakeExitError(RuntimeError):
    pass


def fake_exit(msg=None):
    if msg and isinstance(msg, str):
        print(msg)
    raise FakeExitError()


def supress_exit(msg=''):
    print(msg)


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


def test_markio_cli_show_help_msg_with_empty_args():
    with capture_print() as value:
        with mock.patch('sys.exit', supress_exit):
            main([])
    assert 'markio -h' in value()


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


def test_markio_cmd_shows_source_for_first_language():
    path = os.path.join(DIRECTORY, 'valid-4.md')
    with capture_print() as value:
        with mock.patch('sys.exit', fake_exit):
            main(['src', path])

    assert value() == "print('hello world')\n"


def test_markio_run_works():
    path = os.path.join(DIRECTORY, 'hello-world.md')
    with capture_print() as value:
        with mock.patch('sys.exit', fake_exit):
            main(['run', path, '--lang', 'python3'])

    assert value() == "Hello World!\n"


def test_markio_test_works():
    path = os.path.join(DIRECTORY, 'hello-world.md')
    with capture_print() as value:
        with mock.patch('sys.exit', fake_exit):
            main(['test', path, '--lang', 'python3'])

    assert value() == "Test case 1:\n" \
                      "    Hello World!\n" \
                      "\n" \
                      "All test cases ran successfully!\n"


def test_reading_invalid_markio():
    path = os.path.join(DIRECTORY, 'invalid-0.md')
    with capture_print() as value:
        try:
            with mock.patch('sys.exit', fake_exit):
                main(['src', path, '--lang', 'python3'])
        except FakeExitError:
            pass

    assert value() == "Error in markio file: line 2: title should have an underline formed of '=' characters.\n"


def test_testing_invalid_code():
    path = os.path.join(DIRECTORY, 'invalid-1.md')
    with capture_print() as value:
        try:
            with mock.patch('sys.exit', fake_exit):
                main(['test', path, '--lang', 'python3'])
        except FakeExitError:
            pass

    assert value() == "Error executing testcase\n" \
                      "    @input 0.5;1.5\n" \
                      "Message\n" \
                      "    Traceback (most recent call last)\n" \
                      "      File \"main.py\", line 1, in <module>\n    \n" \
                      "    ValueError: invalid literal for int() with base 10: '0.5'\n"
