import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.helpers import print_json_response, outformat_is_json

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

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint(res['message'])
