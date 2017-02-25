import click

from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.helpers import (
    outformat_is_json, print_json_response, print_table)

from globus_cli.services.auth import lookup_identity_name

from globus_cli.services.transfer import get_client


@click.command('list', help='List of assigned Roles on an Endpoint')
@common_options
@endpoint_id_arg
def role_list(endpoint_id):
    """
    Executor for `globus access endpoint-role-list`
    """
    client = get_client()

    roles = client.endpoint_role_list(endpoint_id)

    if outformat_is_json():
        print_json_response(roles)
    else:
        def principal_str(role):
            principal = role['principal']
            if role['principal_type'] == 'identity':
                principal = lookup_identity_name(principal)
            return principal
        print_table(roles, [('Principal Type', 'principal_type'),
                            ('Role ID', 'id'), ('Principal', principal_str),
                            ('Role', 'role')])
