from cloudshell.networking.cisco.nxos.flows.cisco_nxos_restore_flow import CiscoNXOSRestoreFlow
from cloudshell.networking.cisco.runners.cisco_configuration_runner import CiscoConfigurationRunner


class CiscoNXOSConfigurationRunner(CiscoConfigurationRunner):
    def __init__(self, cli, logger, context, api):
        super(CiscoNXOSConfigurationRunner, self).__init__(cli, logger, context, api)
        self._restore_flow = CiscoNXOSRestoreFlow(self._cli_handler, self._logger)
        self.file_system = "bootflash:"
