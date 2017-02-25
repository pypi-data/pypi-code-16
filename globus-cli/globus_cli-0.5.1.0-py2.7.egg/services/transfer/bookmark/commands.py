import click

from globus_cli.parsing import common_options

from globus_cli.services.transfer.bookmark.list import bookmark_list
from globus_cli.services.transfer.bookmark.create import bookmark_create
from globus_cli.services.transfer.bookmark.delete import bookmark_delete
from globus_cli.services.transfer.bookmark.rename import bookmark_rename
from globus_cli.services.transfer.bookmark.show import bookmark_show
from globus_cli.services.transfer.bookmark.locate import bookmark_locate


@click.group(name='bookmark', help='Manage Endpoint Bookmarks')
@common_options
def bookmark_command():
    pass


bookmark_command.add_command(bookmark_list)
bookmark_command.add_command(bookmark_create)
bookmark_command.add_command(bookmark_delete)
bookmark_command.add_command(bookmark_rename)
bookmark_command.add_command(bookmark_show)
bookmark_command.add_command(bookmark_locate)
