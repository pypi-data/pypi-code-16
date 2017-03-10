"""
    authorization.cli
    ~~~~~~~~~~~~~~~~~
"""
import sys
import click
import crayons
import psycopg2
import authorization_levels
from .map import AuthzMap

valid_levels = {
    l[6:]: getattr(authorization_levels, l) for l in dir(authorization_levels) if l[:6] == 'LEVEL_'
}


@click.group()
@click.option('--debug', is_flag=True)
@click.option('--psql-host', default='localhost', type=str, envvar='DB_HOST')
@click.option('--psql-port', default=5432, type=int, envvar='DB_PORT')
@click.option('--psql-db', default='authz', type=str, envvar='DB_DATABASE')
@click.option('--psql-user', default='authuser', type=str, envvar='DB_USER')
@click.option('--psql-password', default='authpassword', type=str, prompt=True, hide_input=True, envvar='DB_PASS')
@click.pass_context
def cli(ctx, debug, psql_host, psql_port, psql_db, psql_user, psql_password):
    try:
        authzmap = AuthzMap(
            host=psql_host,
            port=psql_port,
            dbname=psql_db,
            user=psql_user,
            password=psql_password
        )
    except psycopg2.OperationalError as e:
        print(crayons.red('Could not connect to the database'))
        if debug:
            raise
        sys.exit(1)
    # create the tables if they don't exist
    authzmap.create()
    ctx.authzmap = authzmap


@cli.group()
@click.argument('user', type=str)
@click.pass_context
def user(ctx, user):
    ctx.user = user
    ctx.authzmap = ctx.parent.authzmap


@user.command()
@click.argument('level', type=click.Choice(valid_levels.keys()))
@click.pass_context
def assign(ctx, level):
    authzmap = ctx.parent.authzmap
    user = ctx.parent.user
    try:
        authzmap[user] = valid_levels[level]
    except ValueError:
        if user in authzmap:
            del authzmap[user]
    print(crayons.green('User {} now has authz level {}'.format(user, level)))


@user.command()
@click.pass_context
def info(ctx):
    authzmap = ctx.parent.authzmap
    user = ctx.parent.user
    if user in authzmap:
        l = authzmap[user]
        level = [k for k in valid_levels if valid_levels[k] == l][0]
        print(crayons.green('User {} has authorization level {}'.format(user, level)))
    else:
        print(crayons.green('User {} has default authorization level'.format(user)))


if __name__ == '__main__':
    cli()
