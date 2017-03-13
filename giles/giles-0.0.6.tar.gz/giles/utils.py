from __future__ import unicode_literals, print_function, absolute_import
import chalk
import getpass
import importlib
import os
import sys


def get_input(prompt, required=False, secret=False):
    output = None
    _input = getpass.getpass if secret else raw_input

    formatted_prompt = chalk.format_txt('white', prompt, None, ['bold'])
    output = _input(formatted_prompt)
    while not output and required:
        output = _input(formatted_prompt)
    return output


def load_subcommands(dot_path):
    importlib.import_module(dot_path)
    module = sys.modules[dot_path]
    path = module.__path__[0]
    for name in os.listdir(os.path.join(path, 'subcommands')):
        if not name.startswith('_') and name.endswith('py'):
            importlib.import_module(
                dot_path + '.subcommands.' + name.replace('.py', '')
            )
