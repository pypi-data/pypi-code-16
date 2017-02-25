import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import (
    common_options, endpoint_id_arg,
    server_add_and_update_opts, server_id_arg)
from globus_cli.helpers import print_json_response, outformat_is_json

from globus_cli.services.transfer.helpers import (
    get_client, assemble_generic_doc)


@click.command('update', help='Update attributes of a Server on an Endpoint')
@common_options
@server_add_and_update_opts
@endpoint_id_arg
@server_id_arg
def server_update(endpoint_id, server_id, subject, port, scheme, hostname):
    """
    Executor for `globus transfer endpoint server update`
    """
    client = get_client()

    server_doc = assemble_generic_doc(
        'server',
        subject=subject, port=port, scheme=scheme, hostname=hostname)

    res = client.update_endpoint_server(endpoint_id, server_id, server_doc)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint(res['message'])
