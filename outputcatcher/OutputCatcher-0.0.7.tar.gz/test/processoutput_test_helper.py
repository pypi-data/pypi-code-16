#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" processoutput_test_helper.py
    Helper for testing ProcessOutput. It simply outputs text to stdout,
    stderr, or both with options to control the text and file.
    -Christopher Welborn 01-15-2017
"""

import os
import sys

NAME = 'ProcessOutput Test Helper'
VERSION = '0.0.1'
VERSIONSTR = '{} v. {}'.format(NAME, VERSION)
SCRIPT = os.path.split(os.path.abspath(sys.argv[0]))[1]
SCRIPTDIR = os.path.abspath(sys.path[0])


def main(args):
    """ Main entry point, expects args from sys. """
    return do_output(args)


def do_output(args):
    """ Just output to the specified file. """
    fs = set()
    if pop_flag_opt(args, ('-o', '--stdout')):
        fs.add(sys.stdout)
    if pop_flag_opt(args, ('-e', '--stderr')):
        fs.add(sys.stderr)
    if pop_flag_opt(args, ('-b', '--both')):
        fs.update((sys.stdout, sys.stderr))
    stdin = pop_flag_opt(args, ('-i', '--stdin'))
    name = pop_flag_opt(args, ('-n', '--name'))
    stream = pop_flag_opt(args, ('-s', '--stream'))
    if stdin:
        msg = sys.stdin.read()
    else:
        msg = ('\n' if stream else ' ').join(args)
    if not msg:
        msg = '{} test line.'.format(NAME)

    def write_line(f, line):
        if name:
            print('{}: {}'.format(f.name, line), file=f)
        else:
            print(line, file=f)

    for f in fs or [sys.stdout]:
        if stream:
            for line in msg.split('\n'):
                write_line(f, line)
        else:
            write_line(f, msg)

    return 0


def pop_flag_opt(lst, opts, default=False):
    """ Pop a flag argument out of an arg list if it exists, otherwise
        return `default`.
    """
    for arg in lst[:]:
        if arg in opts:
            lst.remove(arg)
            return arg
    return default


def print_err(*args, **kwargs):
    """ A wrapper for print() that uses stderr by default. """
    if kwargs.get('file', None) is None:
        kwargs['file'] = sys.stderr
    print(*args, **kwargs)


class InvalidArg(ValueError):
    """ Raised when the user has used an invalid argument. """
    def __init__(self, msg=None):
        self.msg = msg or ''

    def __str__(self):
        if self.msg:
            return 'Invalid argument, {}'.format(self.msg)
        return 'Invalid argument!'


if __name__ == '__main__':
    try:
        mainret = main(sys.argv[1:])
    except InvalidArg as ex:
        print_err(ex)
        mainret = 1
    except (EOFError, KeyboardInterrupt):
        print_err('\nUser cancelled.\n')
        mainret = 2
    except BrokenPipeError:
        print_err('\nBroken pipe, input/output was interrupted.\n')
        mainret = 3
    sys.exit(mainret)
