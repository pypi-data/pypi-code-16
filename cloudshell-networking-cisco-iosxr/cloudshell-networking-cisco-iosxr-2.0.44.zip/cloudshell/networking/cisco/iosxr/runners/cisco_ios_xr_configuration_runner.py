from cloudshell.networking.cisco.flow.cisco_save_flow import CiscoSaveFlow
from cloudshell.networking.cisco.iosxr.cisco_ios_xr_cli_handler import CiscoIOSXRCliHandler
from cloudshell.networking.cisco.iosxr.flows.cisco_ios_xr_restore_flow import CiscoIOSXRRestoreFlow
from cloudshell.networking.devices.runners.configuration_runner import ConfigurationRunner


class CiscoIOSXRConfigurationRunner(ConfigurationRunner):
    def __init__(self, cli, logger, context, api):
        super(CiscoIOSXRConfigurationRunner, self).__init__(logger, context, api)
        self._cli_handler = CiscoIOSXRCliHandler(cli, context, logger, api)
        self._save_flow = CiscoSaveFlow(cli_handler=self._cli_handler,
                                        logger=self._logger)
        self._restore_flow = CiscoIOSXRRestoreFlow(cli_handler=self._cli_handler, logger=self._logger)
        self.file_system = "bootflash:"
