from cloudshell.networking.cisco.autoload.cisco_generic_snmp_autoload import CiscoGenericSNMPAutoload
from cloudshell.networking.cisco.iosxr.autoload.autoload_structure import GenericPort, GenericPortChannel, \
    CiscoIOSXRRouter, GenericChassis, GenericModule, GenericPowerPort


class CiscoIOSXRAutoload(CiscoGenericSNMPAutoload):
    def __init__(self, snmp_handler, logger, supported_os, resource_name):
        super(CiscoIOSXRAutoload, self).__init__(snmp_handler, logger, supported_os, resource_name)
        self.port = GenericPort
        self.power_port = GenericPowerPort
        self.port_channel = GenericPortChannel
        self.root_model = CiscoIOSXRRouter
        self.chassis = GenericChassis
        self.module = GenericModule

    def _get_power_supply_parent_id(self, port):
        parent_id = int(self.entity_table[port]['entPhysicalContainedIn'])
        result = ''
        if parent_id in self.entity_table.keys() and 'entPhysicalClass' in self.entity_table[parent_id]:
            if self.entity_table[parent_id]['entPhysicalClass'] == 'container':
                result = (self._get_power_supply_parent_id(parent_id) +
                          self.entity_table[parent_id]['entPhysicalParentRelPos'])
        return result
