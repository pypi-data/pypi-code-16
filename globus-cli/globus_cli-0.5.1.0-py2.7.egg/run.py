from globus_cli.parsing import globus_main_func

from globus_cli.login import login_command
from globus_cli.list_commands import list_commands
from globus_cli.config_command import config_command
from globus_cli.whoami import whoami_command

from globus_cli.services.auth import auth_command
from globus_cli.services.transfer import transfer_command


@globus_main_func
def main():
    pass


main.add_command(auth_command)
main.add_command(transfer_command)
main.add_command(login_command)
main.add_command(list_commands)
main.add_command(config_command)
main.add_command(whoami_command)
