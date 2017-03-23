from cloudshell.networking.cisco.flow.cisco_autoload_flow import CiscoAutoloadFlow
from cloudshell.networking.cisco.iosxr.autoload.cisco_ios_xr_autoload import CiscoIOSXRAutoload
from cloudshell.networking.cisco.iosxr.cisco_ios_xr_cli_handler import CiscoIOSXRCliHandler
from cloudshell.networking.devices.runners.autoload_runner import AutoloadRunner


class CiscoIOSXRAutoloadRunner(AutoloadRunner):
    def __init__(self, cli, logger, api, context, supported_os):
        super(CiscoIOSXRAutoloadRunner, self).__init__(cli, logger, context, supported_os)
        self._cli_handler = CiscoIOSXRCliHandler(cli, context, logger, api)
        self._logger = logger
        self._autoload_flow = CiscoAutoloadFlow(cli_handler=self._cli_handler,
                                                autoload_class=CiscoIOSXRAutoload,
                                                logger=logger,
                                                resource_name=self._resource_name)
