import importlib
import os
import sys

registry = {}

__module__ = sys.modules[__name__]


def load_modules():
    path = __module__.__path__[0]
    for name in os.listdir(path):
        if not name.startswith('_') and name.endswith('py'):
            importlib.import_module(
                'giles.commands.' + name.replace('.py', '')
            )


load_modules()
