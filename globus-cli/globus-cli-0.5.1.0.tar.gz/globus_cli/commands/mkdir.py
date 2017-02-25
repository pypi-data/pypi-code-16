import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options, ENDPOINT_PLUS_REQPATH
from globus_cli.helpers import outformat_is_json, print_json_response

from globus_cli.services.transfer import get_client, autoactivate


@click.command('mkdir', help='Make a directory on an Endpoint')
@common_options
@click.argument('endpoint_plus_path', metavar=ENDPOINT_PLUS_REQPATH.metavar,
                type=ENDPOINT_PLUS_REQPATH)
def mkdir_command(endpoint_plus_path):
    """
    Executor for `globus mkdir`
    """
    endpoint_id, path = endpoint_plus_path

    client = get_client()
    autoactivate(client, endpoint_id, if_expires_in=60)

    res = client.operation_mkdir(endpoint_id, path=path)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint(res['message'])
