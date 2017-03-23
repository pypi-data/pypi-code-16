from cloudshell.networking.cisco.iosxr.cisco_ios_xr_cli_handler import CiscoIOSXRCliHandler
from cloudshell.networking.devices.runners.state_runner import StateRunner


class CiscoIOSXRStateRunner(StateRunner):
    def __init__(self, cli, logger, api, context):
        """

        :param cli:
        :param logger:
        :param api:
        :param context:
        """

        super(CiscoIOSXRStateRunner, self).__init__(logger, api, context)
        self._cli_handler = CiscoIOSXRCliHandler(cli, context, logger, api)
