import click

from globus_cli.parsing import common_options, endpoint_id_arg, role_id_arg
from globus_cli.helpers import (
    outformat_is_json, print_json_response, colon_formatted_print)

from globus_cli.services.auth import lookup_identity_name

from globus_cli.services.transfer import get_client


@click.command('show', help='Show full info for a Role on an Endpoint')
@common_options
@endpoint_id_arg
@role_id_arg
def role_show(endpoint_id, role_id):
    """
    Executor for `globus endpoint role show`
    """
    client = get_client()

    role = client.get_endpoint_role(endpoint_id, role_id)

    if outformat_is_json():
        print_json_response(role)
    else:
        formattable_doc = {
            'principal_type': role['principal_type'],
            'principal': lookup_identity_name(role['principal']),
            'role': role['role']
        }
        named_fields = (('Principal Type', 'principal_type'),
                        ('Principal', 'principal'), ('Role', 'role'))
        colon_formatted_print(formattable_doc, named_fields)
