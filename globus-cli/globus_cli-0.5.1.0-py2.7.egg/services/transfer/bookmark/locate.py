import click

from globus_cli.parsing import common_options
from globus_cli.services.transfer.helpers import get_client
from globus_cli.services.transfer.bookmark.helpers import resolve_id_or_name


@click.command('locate', help=('Output <UUID>:<path> of a bookmark; useful in '
                               'a subshell as input to another command'),
               short_help="Lookup Bookmark for use in subshells")
@common_options
@click.argument('bookmark_id_or_name')
def bookmark_locate(bookmark_id_or_name):
    """
    Executor for `globus transfer bookmark locate`
    """
    client = get_client()
    res = resolve_id_or_name(client, bookmark_id_or_name)
    print('{}:{}'.format(res['endpoint_id'], res['path']))
