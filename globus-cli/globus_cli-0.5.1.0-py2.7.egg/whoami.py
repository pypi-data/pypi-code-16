import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options
from globus_cli.config import (
    WHOAMI_ID_OPTNAME, WHOAMI_USERNAME_OPTNAME,
    WHOAMI_EMAIL_OPTNAME, WHOAMI_NAME_OPTNAME,
    GLOBUS_ENV, lookup_option)


@click.command('whoami',
               help=('Show the currently logged-in identity.'))
@common_options(no_format_option=True, no_map_http_status_option=True)
@click.option('--verbose', '-v', is_flag=True, default=False)
def whoami_command(verbose):
    """
    Executor for `globus whoami`
    """

    username = lookup_option(WHOAMI_USERNAME_OPTNAME,
                             environment=GLOBUS_ENV)
    if not username:
        safeprint('No login information available. Please try '
                  'logging in again.')
        return

    safeprint('Logged in as: {}'.format(username))

    if verbose:
        name = lookup_option(WHOAMI_NAME_OPTNAME, environment=GLOBUS_ENV)
        identity_id = lookup_option(WHOAMI_ID_OPTNAME, environment=GLOBUS_ENV)
        email = lookup_option(WHOAMI_EMAIL_OPTNAME, environment=GLOBUS_ENV)

        safeprint('Name: {}'.format(name))
        safeprint('Id: {}'.format(identity_id))
        safeprint('Email: {}'.format(email))
