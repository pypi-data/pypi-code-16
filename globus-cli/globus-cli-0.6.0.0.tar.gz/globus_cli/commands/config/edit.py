import click
import os
import subprocess

from globus_cli.parsing import common_options


@click.command('edit', help='Edit your Globus Config file')
@common_options(no_format_option=True)
def edit_command():
    """
    Executor for `globus config edit`
    """
    editor = os.environ.get('EDITOR', 'nano')
    os.umask(0o077)
    subprocess.call([editor, os.path.expanduser('~/.globus.cfg')])
