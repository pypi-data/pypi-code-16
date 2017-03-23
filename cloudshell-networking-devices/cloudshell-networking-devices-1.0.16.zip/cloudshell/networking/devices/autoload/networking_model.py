from cloudshell.networking.devices.autoload.model.generic_resource import GenericResource
from cloudshell.networking.devices.autoload.networking_attributes import ChassisAttributes, \
    PowerPortAttributes, PortAttributes, ModuleAttributes, SubModuleAttributes, PortChannelAttributes, \
    RootAttributes
from cloudshell.shell.core.driver_context import AutoLoadDetails


class RootElement(GenericResource):
    ATTRIBUTE_CONTAINER = RootAttributes
    MODEL = None
    NAME_TEMPLATE = None
    RELATIVE_PATH_TEMPLATE = None

    def __init__(self, element_id=None, **attributes_dict):
        GenericResource.__init__(self, element_id, **attributes_dict)
        self.chassis = []
        self.port_channels = []

    def build_relative_path(self, parent_path=None):
        GenericResource.build_relative_path(self, parent_path)
        self._validate_child_ids(self.chassis)
        self._validate_child_ids(self.port_channels)
        self._build_relative_path_for_child_resources(self.chassis, self.port_channels)

    def get_resources(self):
        return self._get_resources_for_child_resources(self.chassis, self.port_channels)

    def get_attributes(self):
        return GenericResource.get_attributes(self) + self._get_attributes_for_child_resources(self.chassis,
                                                                                               self.port_channels)

    def get_autoload_details(self):
        self.build_relative_path()
        return AutoLoadDetails(self.get_resources(), self.get_attributes())


class Chassis(GenericResource):
    ATTRIBUTE_CONTAINER = ChassisAttributes
    MODEL = 'Generic Chassis'
    NAME_TEMPLATE = 'Chassis{0}'
    RELATIVE_PATH_TEMPLATE = '{0}'

    def __init__(self, element_id, **kwargs):
        GenericResource.__init__(self, element_id, **kwargs)
        self.modules = []
        self.ports = []
        self.power_ports = []

    def build_relative_path(self, parent_path):
        GenericResource.build_relative_path(self, parent_path)
        self._validate_child_ids(self.modules, self.ports)
        self._validate_child_ids(self.power_ports)
        self._build_relative_path_for_child_resources(self.modules, self.ports, self.power_ports)

    def get_attributes(self, *args):
        return GenericResource.get_attributes(self) + self._get_attributes_for_child_resources(self.modules, self.ports,
                                                                                               self.power_ports)

    def get_resources(self):
        return GenericResource.get_resources(self) + self._get_resources_for_child_resources(self.modules, self.ports,
                                                                                             self.power_ports)


class PowerPort(GenericResource):
    ATTRIBUTE_CONTAINER = PowerPortAttributes
    MODEL = 'Generic Power Port'
    NAME_TEMPLATE = 'PP{0}'
    RELATIVE_PATH_TEMPLATE = '{0}/PP{1}'

    def __init__(self, element_id, **kwargs):
        GenericResource.__init__(self, element_id, **kwargs)


class Port(GenericResource):
    ATTRIBUTE_CONTAINER = PortAttributes
    MODEL = 'Generic Port'
    NAME_TEMPLATE = '{0}'
    RELATIVE_PATH_TEMPLATE = '{0}/{1}'

    def __init__(self, element_id, name, **kwargs):
        GenericResource.__init__(self, element_id, name=name, **kwargs)


class PortChannel(GenericResource):
    ATTRIBUTE_CONTAINER = PortChannelAttributes
    MODEL = 'Generic Port Channel'
    NAME_TEMPLATE = '{0}'
    RELATIVE_PATH_TEMPLATE = 'PC{0}'

    def __init__(self, element_id, name, **kwargs):
        GenericResource.__init__(self, element_id, name=name, **kwargs)


class Module(GenericResource):
    ATTRIBUTE_CONTAINER = ModuleAttributes
    MODEL = 'Generic Module'
    NAME_TEMPLATE = 'Module{0}'
    RELATIVE_PATH_TEMPLATE = '{0}/{1}'

    def __init__(self, element_id, **kwargs):
        GenericResource.__init__(self, element_id, **kwargs)
        self.sub_modules = []
        self.ports = []

    def build_relative_path(self, parent_path):
        GenericResource.build_relative_path(self, parent_path)
        self._validate_child_ids(self.sub_modules, self.ports)
        self._build_relative_path_for_child_resources(self.sub_modules, self.ports)

    def get_resources(self):
        return GenericResource.get_resources(self) + self._get_resources_for_child_resources(self.sub_modules,
                                                                                             self.ports)

    def get_attributes(self):
        return GenericResource.get_attributes(self) + self._get_attributes_for_child_resources(self.sub_modules,
                                                                                               self.ports)


class SubModule(GenericResource):
    ATTRIBUTE_CONTAINER = SubModuleAttributes
    MODEL = 'Generic Sub Module'
    NAME_TEMPLATE = 'SubModule{0}'
    RELATIVE_PATH_TEMPLATE = '{0}/{1}'

    def __init__(self, element_id, **kwargs):
        GenericResource.__init__(self, element_id, **kwargs)
        self.ports = []

    def build_relative_path(self, parent_path):
        GenericResource.build_relative_path(self, parent_path)
        self._validate_child_ids(self.ports)
        self._build_relative_path_for_child_resources(self.ports)

    def get_resources(self):
        return GenericResource.get_resources(self) + self._get_resources_for_child_resources(self.ports)

    def get_attributes(self):
        return GenericResource.get_attributes(self) + self._get_attributes_for_child_resources(self.ports)
