import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options
from globus_cli.helpers import colon_formatted_print
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

    if verbose:
        fields = tuple((x, x) for x in ('Username', 'Name', 'ID', 'Email'))
        user_doc = {
            'Username': username,
            'Name': lookup_option(WHOAMI_NAME_OPTNAME, environment=GLOBUS_ENV),
            'ID': lookup_option(WHOAMI_ID_OPTNAME, environment=GLOBUS_ENV),
            'Email': lookup_option(WHOAMI_EMAIL_OPTNAME,
                                   environment=GLOBUS_ENV)
        }
        colon_formatted_print(user_doc, fields)
    else:
        safeprint(username)
