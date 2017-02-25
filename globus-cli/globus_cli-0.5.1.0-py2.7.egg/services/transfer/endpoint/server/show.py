import click

from globus_cli.parsing import (
    common_options, endpoint_id_arg, server_id_arg)
from globus_cli.helpers import (
    print_json_response, outformat_is_json, colon_formatted_print)

from globus_cli.services.transfer.helpers import get_client


@click.command('show', help='Show a server belonging to an Endpoint')
@common_options
@endpoint_id_arg
@server_id_arg
def server_show(endpoint_id, server_id):
    """
    Executor for `globus transfer endpoint server show`
    """
    client = get_client()

    server_doc = client.get_endpoint_server(endpoint_id, server_id)

    if outformat_is_json():
        print_json_response(server_doc)
    else:
        fields = (('ID', 'id'), ('URI', 'uri'), ('Subject', 'subject'))
        colon_formatted_print(server_doc, fields)
