from cloudshell.networking.cisco.iosxr.cisco_ios_xr_cli_handler import CiscoIOSXRCliHandler
from cloudshell.networking.devices.runners.run_command_runner import RunCommandRunner


class CiscoIOSXRRunCommandRunner(RunCommandRunner):
    def __init__(self, cli, context, logger, api):
        """Create CiscoRunCommandOperations

        :param context: command context
        :param api: cloudshell api object
        :param cli: CLI object
        :param logger: QsLogger object
        :return:
        """

        super(CiscoIOSXRRunCommandRunner, self).__init__(logger)
        self._cli_handler = CiscoIOSXRCliHandler(cli, context, logger, api)
