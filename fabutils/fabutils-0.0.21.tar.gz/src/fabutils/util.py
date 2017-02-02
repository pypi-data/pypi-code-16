# -*- coding: utf-8 -*-
"""
Various utilities and helpers.
"""
from __future__ import absolute_import, print_function


def sysmsg(msg, *args, **kw):
    """ Print sys message to stdout.

    System messages should inform about the flow of the script. This should
    be a major milestones during the build. For a per step status messages
    use ``infomsg``.
    """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)
    print('-- \033[32m{}\033[0m'.format(msg))


def infomsg(msg, *args, **kw):
    """ Per step status messages

    Use this locally in a command definition to highlight more important
    information.
    """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)
    print('-- \033[1m{}\033[0m'.format(msg))


def errmsg(msg, *args, **kw):
    """ Per step status messages

    Use this locally in a command definition to highlight more important
    information.
    """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)
    print('-- \033[31m{}\033[0m'.format(msg))
