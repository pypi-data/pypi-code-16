import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options
from globus_cli.helpers import outformat_is_json, print_json_response

from globus_cli.services.transfer import get_client


@click.command('delete', help='Delete a Bookmark')
@common_options
@click.argument('bookmark_id')
def bookmark_delete(bookmark_id):
    """
    Executor for `globus bookmark delete`
    """
    client = get_client()

    res = client.delete_bookmark(bookmark_id)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint(res['message'])
