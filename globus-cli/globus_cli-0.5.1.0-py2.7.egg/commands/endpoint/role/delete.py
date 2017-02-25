import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options, endpoint_id_arg, role_id_arg
from globus_cli.helpers import outformat_is_json, print_json_response

from globus_cli.services.transfer import get_client


@click.command('delete', help='Remove a Role from an Endpoint')
@common_options
@endpoint_id_arg
@role_id_arg
def role_delete(role_id, endpoint_id):
    """
    Executor for `globus endpoint role delete`
    """
    client = get_client()

    res = client.delete_endpoint_role(endpoint_id, role_id)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint(res['message'])
