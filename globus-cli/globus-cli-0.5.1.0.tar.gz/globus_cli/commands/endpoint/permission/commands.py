import click

from globus_cli.parsing import common_options

from globus_cli.commands.endpoint.permission.list import list_command
from globus_cli.commands.endpoint.permission.create import create_command
from globus_cli.commands.endpoint.permission.show import show_command
from globus_cli.commands.endpoint.permission.update import update_command
from globus_cli.commands.endpoint.permission.delete import delete_command


@click.group(name='permission', help=('Manage Endpoint Permissions '
                                      '(Access Control Lists)'))
@common_options
def permission_command():
    pass


permission_command.add_command(list_command)
permission_command.add_command(create_command)
permission_command.add_command(show_command)
permission_command.add_command(update_command)
permission_command.add_command(delete_command)
