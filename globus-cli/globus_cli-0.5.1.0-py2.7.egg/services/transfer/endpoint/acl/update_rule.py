import click

from globus_cli.parsing import (
    CaseInsensitiveChoice, common_options, endpoint_id_arg)
from globus_cli.helpers import print_json_response

from globus_cli.services.transfer.helpers import (
    get_client, assemble_generic_doc)


@click.command('update-rule', help='Update an ACL rule')
@endpoint_id_arg
@common_options
@click.argument('rule_id')
@click.option('--permissions', required=True,
              type=CaseInsensitiveChoice(('r', 'rw')),
              help='Permissions to add. Read-Only or Read/Write')
def update_acl_rule(permissions, rule_id, endpoint_id):
    """
    Executor for `globus transfer access update-acl-rule`
    """
    client = get_client()

    rule_data = assemble_generic_doc('access', permissions=permissions)
    res = client.update_endpoint_acl_rule(endpoint_id, rule_id, rule_data)
    print_json_response(res)
