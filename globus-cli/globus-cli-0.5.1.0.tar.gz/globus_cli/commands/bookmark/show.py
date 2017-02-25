import click

from globus_cli.parsing import common_options
from globus_cli.helpers import (
    outformat_is_json, print_json_response, colon_formatted_print)

from globus_cli.services.transfer import get_client
from globus_cli.commands.bookmark.helpers import resolve_id_or_name


@click.command('show', help='Show a Bookmark by either name or ID')
@common_options
@click.argument('bookmark_id_or_name')
def bookmark_show(bookmark_id_or_name):
    """
    Executor for `globus bookmark show`
    """
    client = get_client()
    res = resolve_id_or_name(client, bookmark_id_or_name)

    if outformat_is_json():
        print_json_response(res)
    else:
        fields = (('ID', 'id'), ('Name', 'name'),
                  ('Endpoint ID', 'endpoint_id'), ('Path', 'path'))
        colon_formatted_print(res, fields)
