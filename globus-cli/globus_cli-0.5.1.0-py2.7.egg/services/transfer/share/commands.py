import click

from globus_cli.parsing import common_options

from globus_cli.services.transfer.share.show import share_show
from globus_cli.services.transfer.share.create import share_create
from globus_cli.services.transfer.share.update import share_update
from globus_cli.services.transfer.share.delete import share_delete


@click.group(name='share', help='Manage Globus Share definitions')
@common_options
def share_command():
    pass


share_command.add_command(share_show)
share_command.add_command(share_create)
share_command.add_command(share_update)
share_command.add_command(share_delete)
