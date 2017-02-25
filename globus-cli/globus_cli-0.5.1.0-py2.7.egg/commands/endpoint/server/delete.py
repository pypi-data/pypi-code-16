import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options, endpoint_id_arg, server_id_arg
from globus_cli.helpers import print_json_response, outformat_is_json

from globus_cli.services.transfer import get_client


@click.command('delete', help='Delete a server belonging to an Endpoint')
@common_options
@endpoint_id_arg
@server_id_arg
def server_delete(endpoint_id, server_id):
    """
    Executor for `globus endpoint server show`
    """
    client = get_client()

    server_doc = client.delete_endpoint_server(endpoint_id, server_id)

    if outformat_is_json():
        print_json_response(server_doc)
    else:
        safeprint(server_doc['message'])
