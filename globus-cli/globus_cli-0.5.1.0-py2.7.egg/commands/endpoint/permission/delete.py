import click

from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.helpers import print_json_response

from globus_cli.services.transfer import get_client


@click.command('delete', help=('Delete an access control rule, removing '
                               'permissions'))
@common_options
@endpoint_id_arg
@click.argument('rule_id')
def delete_command(endpoint_id, rule_id):
    """
    Executor for `globus endpoint permission delete`
    """
    client = get_client()

    res = client.delete_endpoint_acl_rule(endpoint_id, rule_id)

    print_json_response(res)
