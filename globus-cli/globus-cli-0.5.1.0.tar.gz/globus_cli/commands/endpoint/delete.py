import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.helpers import outformat_is_json, print_json_response

from globus_cli.services.transfer import get_client


@click.command('delete', help='Delete a given Endpoint')
@common_options
@endpoint_id_arg
def endpoint_delete(endpoint_id):
    """
    Executor for `globus endpoint delete`
    """
    client = get_client()

    res = client.delete_endpoint(endpoint_id)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint(res['message'])
