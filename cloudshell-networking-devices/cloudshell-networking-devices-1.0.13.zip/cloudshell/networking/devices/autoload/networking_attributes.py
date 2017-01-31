from cloudshell.networking.devices.autoload.model.attribute_container import AttributeContainer


class RootAttributes(AttributeContainer):
    VENDOR = 'Vendor'
    SYSTEM_NAME = 'System Name'
    LOCATION = 'Location'
    CONTACT_NAME = 'Contact Name'
    OS_VERSION = 'OS Version'
    MODEL = 'Model'


class ChassisAttributes(AttributeContainer):
    SERIAL_NUMBER = 'Serial Number'
    MODEL = 'Model'


class ModuleAttributes(AttributeContainer):
    SERIAL_NUMBER = 'Serial Number'
    MODEL = 'Model'
    VERSION = 'Version'


class SubModuleAttributes(AttributeContainer):
    SERIAL_NUMBER = 'Serial Number'
    MODEL = 'Model'
    VERSION = 'Version'


class PortAttributes(AttributeContainer):
    PORT_DESCRIPTION = 'Port Description'
    L2_PROTOCOL_TYPE = 'L2 Protocol Type'
    MAC_ADDRESS = 'MAC Address'
    MTU = 'MTU'
    DUPLEX = 'Duplex'
    AUTO_NEGOTIATION = 'Auto Negotiation'
    BANDWIDTH = 'Bandwidth'
    ADJACENT = 'Adjacent'
    IPV4_ADDRESS = 'IPv4 Address'
    IPV6_ADDRESS = 'IPv6 Address'

    def __init__(self, relative_path, **kwargs):
        self._DEFAULT_VALUES[self.L2_PROTOCOL_TYPE] = 'ethernet'
        self._DEFAULT_VALUES[self.MTU] = 0
        self._DEFAULT_VALUES[self.BANDWIDTH] = 0
        self._DEFAULT_VALUES[self.DUPLEX] = 'Full'
        super(PortAttributes, self).__init__(relative_path, **kwargs)


class PortChannelAttributes(AttributeContainer):
    PORT_DESCRIPTION = 'Port Description'
    ASSOCIATED_PORTS = 'Associated Ports'
    IPV4_ADDRESS = 'IPv4 Address'
    IPV6_ADDRESS = 'IPv6 Address'

    def __init__(self, relative_path, **kwargs):
        super(PortChannelAttributes, self).__init__(relative_path, **kwargs)


class PowerPortAttributes(AttributeContainer):
    SERIAL_NUMBER = 'Serial Number'
    MODEL = 'Model'
    VERSION = 'Version'
    PORT_DESCRIPTION = 'Port Description'
