import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options
from globus_cli.helpers import outformat_is_json, print_json_response

from globus_cli.services.transfer import get_client


@click.command('rename', help='Change a Bookmark\'s name')
@common_options
@click.argument('bookmark_id')
@click.argument('new_bookmark_name')
def bookmark_rename(bookmark_id, new_bookmark_name):
    """
    Executor for `globus bookmark rename`
    """
    client = get_client()

    submit_data = {
        'name': new_bookmark_name
    }

    res = client.update_bookmark(bookmark_id, submit_data)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint('Success')
