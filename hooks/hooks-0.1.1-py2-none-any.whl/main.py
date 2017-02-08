"""
hooks - git hooks

Usage:
    hooks <COMMAND> [<args>...]
    hooks -h | --help

Commands:
    install  Install the hooks into the current git repository
    ls       List the installed git hooks
    update   Bring the hooks up-to-date
"""

import sys
from docopt import docopt
from hooks import commands


__version__ = '0.1'


def cli():
    arguments = docopt(__doc__, version=__version__, options_first=True)
    command = arguments.pop('<COMMAND>')
    command_fn = getattr(commands, command)
    assert command_fn is not None
    command_args = arguments.pop('<args>') or {}
    sys.exit(command_fn(docopt(command_fn.__doc__, argv=command_args)))
