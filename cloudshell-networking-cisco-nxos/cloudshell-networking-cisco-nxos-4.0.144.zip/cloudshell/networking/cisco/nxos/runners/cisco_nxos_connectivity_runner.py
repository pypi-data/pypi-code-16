from cloudshell.networking.cisco.flow.cisco_add_vlan_flow import CiscoAddVlanFlow
from cloudshell.networking.cisco.runners.cisco_connectivity_runner import CiscoConnectivityRunner


class CiscoNXOSConnectivityRunner(CiscoConnectivityRunner):
    def __init__(self, cli, logger, api, context):
        super(CiscoNXOSConnectivityRunner, self).__init__(cli, logger, api, context)
        self.add_vlan_flow = CiscoAddVlanFlow(cli_handler=self._cli_handler,
                                              logger=self._logger, does_require_single_switchport_cmd=True)
