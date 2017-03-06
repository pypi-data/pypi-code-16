import sys
import os.path
import os
from os.path import join as pjoin
from IPython import embed
import json

import click
from appdirs import AppDirs

import axsemantics
from axsemantics import AuthenticationError

from .common import CliData, pass_data


def _config_dir(filename=''):
    dirs = AppDirs('axsemantics', 'AXSemantics')
    if not os.path.isdir(dirs.user_config_dir):
        os.makedirs(dirs.user_config_dir)
    if filename:
        return pjoin(dirs.user_config_dir, filename)
    return dirs.user_config_dir


class TokenFile:

    def __init__(self, filename=None):
        self.filename = filename

    def exists(self):
        return os.path.exists(_config_dir(self.filename))

    def read(self):
        token_file = _config_dir(self.filename)
        if not os.path.isfile(token_file):
            return ''
        with open(token_file, 'r') as f:
            return f.read()

    def write(self, token):
        token_file = _config_dir(self.filename)
        with open(token_file, 'w') as f:
            f.write(token)

    def delete(self):
        token_file = _config_dir(self.filename)
        if os.path.isfile(token_file):
            os.unlink(token_file)



@click.group()
# @click.option('--login', '-l', help='login email', prompt=True, envvar='AXSEMANTICS_LOGIN')
# @click.option('--password', '-p', help='login password',
#               prompt=True, hide_input=True, envvar='AXSEMANTICS_PASSWORD')
@click.option('--refresh-token', '-t', help='AXSemantics Refresh Token', envvar='AXSEMANTICS_REFRESH_TOKEN')
@click.pass_context
def cli(ctx, refresh_token):
    ctx.obj = {}
    ctx.obj['refresh_token'] = ''
    token_file = TokenFile('refresh_token')
    ctx.obj['refresh_token_file'] = token_file
    if refresh_token is not None:
        ctx.obj['refresh_token'] = refresh_token
    else:
        if token_file.exists():
            ctx.obj['refresh_token'] = token_file.read()
        else:
            if ctx.invoked_subcommand not in ('login', 'logout'):
                sys.exit('not logged in')
    try:
        axsemantics.login(ctx.obj['refresh_token'])
    except AuthenticationError:
        if ctx.invoked_subcommand not in ('login', 'logout'):
            sys.exit('login failed')
    # ctx.obj['id_token_file'] = TokenFile('id_token')


@cli.command('login')
@click.pass_context
@click.argument('token')
def login(ctx, token):
    try:
        axsemantics.login(token)
        ctx.obj['refresh_token'] = token
        ctx.obj['refresh_token_file'].write(token)
    except AuthenticationError:
        sys.exit('login failed')


@cli.command('logout')
@click.pass_context
def logout(ctx):
    ctx.obj['refresh_token'] = ''
    ctx.obj['refresh_token_file'].delete()


@cli.command('whoami')
@click.pass_context
def whoami(ctx):
    from axsemantics.net import RequestHandler
    from axsemantics import constants
    requestor = RequestHandler(token=constants.API_TOKEN)
    r = requestor.request('get', '/v1/me/', None)
    print('''First Name: {first_name}
Last Name: {last_name}
Username: {username}
Email: {email}'''.format(first_name=r[0]['first_name'],
                         last_name=r[0]['last_name'],
                         username=r[0]['username'],
                         email=r[0]['email']))


from .content_project import content_project
cli.add_command(content_project)


from .training import training
cli.add_command(training)


from .data_importer import new_importer
cli.add_command(new_importer)
