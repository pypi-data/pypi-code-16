import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options, ENDPOINT_PLUS_REQPATH
from globus_cli.helpers import outformat_is_json, print_json_response

from globus_cli.services.transfer import get_client


@click.command('create', help='Create a Bookmark for the current user')
@common_options
@click.argument('endpoint_plus_path', metavar=ENDPOINT_PLUS_REQPATH.metavar,
                type=ENDPOINT_PLUS_REQPATH)
@click.argument('bookmark_name')
def bookmark_create(endpoint_plus_path, bookmark_name):
    """
    Executor for `globus bookmark create`
    """
    endpoint_id, path = endpoint_plus_path
    client = get_client()

    submit_data = {
        'endpoint_id': str(endpoint_id),
        'path': path,
        'name': bookmark_name
    }

    res = client.create_bookmark(submit_data)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint('Bookmark ID: {}'.format(res['id']))
