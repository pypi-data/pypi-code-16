import base64
import uuid

import click

from globus_cli.parsing import common_options, HiddenOption
from globus_cli.helpers import (
    print_json_response, outformat_is_json, print_table)

from globus_cli.services.auth import get_auth_client


_USERNAMES_STYLE = 'usernames'
_IDS_STYLE = 'identities'

_HIDDEN_TRANSFER_STYLE = 'globus-transfer'


def _b32_decode(v):
    assert v.startswith('u_'), "{0} didn't start with 'u_'".format(v)
    v = v[2:]
    assert len(v) == 26, "u_{0} is the wrong length".format(v)
    # append padding and uppercase so that b32decode will work
    v = v.upper() + 6*'='
    return str(uuid.UUID(bytes=base64.b32decode(v)))


@click.command('get-identities', help='Lookup Globus Auth Identities')
@common_options
@click.option('--usernames', 'lookup_style', default=True,
              help=('Values are Usernames to lookup in Globus Auth. '
                    'This is the default behavior'),
              flag_value=_USERNAMES_STYLE)
@click.option('--identities', 'lookup_style',
              help='Values are Identity IDs to lookup in Globus Auth',
              flag_value=_IDS_STYLE)
@click.option('--globus-transfer-decode', 'lookup_style', cls=HiddenOption,
              flag_value=_HIDDEN_TRANSFER_STYLE)
@click.argument('values', required=True, nargs=-1)
def get_identities_command(values, lookup_style):
    """
    Executor for `globus get-identities`
    """
    client = get_auth_client()

    params = {}

    # set commandline params if passed
    if lookup_style == _USERNAMES_STYLE:
        params['usernames'] = ','.join(values)
    elif lookup_style == _IDS_STYLE:
        params['ids'] = ','.join(values)
    elif lookup_style == _HIDDEN_TRANSFER_STYLE:
        params['ids'] = ','.join(_b32_decode(v) for v in values)

    res = client.get_identities(**params)

    if outformat_is_json():
        print_json_response(res)
    else:
        ids = res['identities']

        print_table(ids, [('ID', 'id'), ('Username', 'username'),
                          ('Full Name', 'name'),
                          ('Organization', 'organization'),
                          ('Email Address', 'email')])
