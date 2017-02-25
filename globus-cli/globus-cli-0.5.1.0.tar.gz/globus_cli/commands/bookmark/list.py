import click

from globus_cli.parsing import common_options
from globus_cli.helpers import outformat_is_json, print_table

from globus_cli.services.transfer import (
    print_json_from_iterator, get_client, display_name_or_cname)


@click.command('list', help='List Bookmarks for the current user')
@common_options
def bookmark_list():
    """
    Executor for `globus bookmark list`
    """
    client = get_client()

    bookmark_iterator = client.bookmark_list()

    def get_ep_name(item):
        ep_id = item['endpoint_id']
        ep_doc = client.get_endpoint(ep_id)
        return display_name_or_cname(ep_doc)

    if outformat_is_json():
        print_json_from_iterator(bookmark_iterator)
    else:
        print_table(bookmark_iterator, [
            ('Name', 'name'),
            ('Bookmark ID', 'id'),
            ('Endpoint ID', 'endpoint_id'),
            ('Endpoint Name', get_ep_name),
            ('Path', 'path')])
