from cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload import CiscoGenericSNMPAutoload
from cloudshell.networking.cisco.nxos.autoload.autoload_structure import GenericPort, GenericPortChannel, \
    CiscoNXOSSwitch, GenericChassis, GenericModule, GenericPowerPort


class CiscoNXOSAutoload(CiscoGenericSNMPAutoload):
    def __init__(self, snmp_handler, logger, supported_os, resource_name):
        super(CiscoNXOSAutoload, self).__init__(snmp_handler, logger, supported_os, resource_name)
        self.port = GenericPort
        self.power_port = GenericPowerPort
        self.port_channel = GenericPortChannel
        self.root_model = CiscoNXOSSwitch
        self.chassis = GenericChassis
        self.module = GenericModule
