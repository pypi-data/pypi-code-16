import click

from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.helpers import (
    outformat_is_json, print_json_response, colon_formatted_print)
from globus_cli.services.auth import lookup_identity_name
from globus_cli.services.transfer import get_client


def _shared_with_keyfunc(rule):
    if rule['principal_type'] == 'identity':
        return lookup_identity_name(rule['principal'])
    elif rule['principal_type'] == 'group':
        return ('https://www.globus.org/app/groups/{}'
                .format(rule['principal']))
    else:
        return rule['principal_type']


@click.command('show', help='Show a Permission on an Endpoint')
@common_options
@endpoint_id_arg
@click.argument('rule_id')
def show_command(endpoint_id, rule_id):
    """
    Executor for `globus endpoint permission show`
    """
    client = get_client()

    rule = client.get_endpoint_acl_rule(endpoint_id, rule_id)

    if outformat_is_json():
        print_json_response(rule)
    else:
        fields = (('Rule ID', 'id'), ('Permissions', 'permissions'),
                  ('Shared With', _shared_with_keyfunc), ('Path', 'path'))
        colon_formatted_print(rule, fields)
