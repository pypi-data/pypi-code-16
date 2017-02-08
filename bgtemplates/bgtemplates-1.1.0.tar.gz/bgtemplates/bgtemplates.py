import click
import logging

from bgtemplates.templates.base import base
from bgtemplates.templates.pydata import pydata
from . import __version__

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--debug', default=False, is_flag=True, help='Give more output (verbose)')
@click.version_option(version=__version__)
def cli(debug):
    """Create a project from one of our templates"""
    if debug:
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG, datefmt='%H:%M:%S')
    else:
        logging.basicConfig(format='... %(message)s', level=logging.INFO)
    logging.debug('Debug mode enabled')


cli.add_command(base)
cli.add_command(pydata)