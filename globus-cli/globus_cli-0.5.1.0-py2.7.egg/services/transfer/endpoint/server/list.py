import click

from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.helpers import print_table, outformat_is_json
from globus_cli.services.transfer.helpers import (
    get_client, print_json_from_iterator)


@click.command('list', help='List all servers belonging to an Endpoint')
@common_options
@endpoint_id_arg
def server_list(endpoint_id):
    """
    Executor for `globus transfer endpoint server list`
    """
    client = get_client()

    server_iterator = client.endpoint_server_list(endpoint_id)

    if outformat_is_json():
        print_json_from_iterator(server_iterator)
    else:
        print_table(server_iterator, [('ID', 'id'), ('URI', 'uri')])
