# -*- coding: utf-8 -*-
import glob
from contextlib import contextmanager
from tempfile import NamedTemporaryFile

import click


click.disable_unicode_literals_warning = True


@click.group('virtualenv')
def main():
    pass


@main.command()
@click.argument('name')
@click.option('--python', default='python2')  # , options=('python2', 'python3'))
def create(name, python):
    """
    Create a virtualenv, caching when possible.
    """
    import os
    from virtualenvapi.manage import VirtualEnvironment

    venv_path = os.path.expandvars('${{WORKON_HOME}}/{}'.format(name))
    venv = VirtualEnvironment(venv_path, python=python)
    venv.open_or_create()
    venv.install('virtualenvwrapper')
