import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import (
    common_options, endpoint_id_arg, server_add_and_update_opts)
from globus_cli.helpers import print_json_response, outformat_is_json

from globus_cli.services.transfer.helpers import (
    get_client, assemble_generic_doc)


@click.command('add', help='Add a server to an Endpoint')
@common_options
@server_add_and_update_opts(add=True)
@endpoint_id_arg
def server_add(endpoint_id, subject, port, scheme, hostname):
    """
    Executor for `globus transfer endpoint server add`
    """
    client = get_client()

    server_doc = assemble_generic_doc(
        'server',
        subject=subject, port=port, scheme=scheme, hostname=hostname)

    res = client.add_endpoint_server(endpoint_id, server_doc)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint(res['message'])
        safeprint('ID: {}'.format(res['id']))
