import base64
import uuid

import click

from globus_sdk import GlobusResponse

from globus_cli.parsing import common_options, HiddenOption
from globus_cli.helpers import (
    print_json_response, outformat_is_json, print_table)

from globus_cli.services.auth import get_auth_client


_HIDDEN_TRANSFER_STYLE = 'globus-transfer'


def _b32_decode(v):
    assert v.startswith('u_'), "{0} didn't start with 'u_'".format(v)
    v = v[2:]
    assert len(v) == 26, "u_{0} is the wrong length".format(v)
    # append padding and uppercase so that b32decode will work
    v = v.upper() + (6 * '=')
    return str(uuid.UUID(bytes=base64.b32decode(v)))


@click.command('get-identities', help='Lookup Globus Auth Identities')
@common_options
@click.option('--globus-transfer-decode', 'lookup_style', cls=HiddenOption,
              flag_value=_HIDDEN_TRANSFER_STYLE)
@click.argument('values', required=True, nargs=-1)
def get_identities_command(values, lookup_style):
    """
    Executor for `globus get-identities`
    """
    client = get_auth_client()

    # set commandline params if passed
    if lookup_style == _HIDDEN_TRANSFER_STYLE:
        res = client.get_identities(
            ids=','.join(_b32_decode(v) for v in values))
    else:
        params = dict(ids=[], usernames=[])
        for val in values:
            try:
                uuid.UUID(val)
                params['ids'].append(val)
            except ValueError:
                params['usernames'].append(val)

        results = []
        for k, v in params.items():
            if not v:
                continue
            results = results + \
                client.get_identities(**{k: ','.join(v)}).data['identities']
        res = GlobusResponse({'identities': results})

    if outformat_is_json():
        print_json_response(res)
    else:
        ids = res['identities']

        print_table(ids, [('ID', 'id'), ('Username', 'username'),
                          ('Full Name', 'name'),
                          ('Organization', 'organization'),
                          ('Email Address', 'email')])
