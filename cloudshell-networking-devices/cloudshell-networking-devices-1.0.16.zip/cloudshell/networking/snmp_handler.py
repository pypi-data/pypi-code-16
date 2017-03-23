from abc import abstractmethod
from cloudshell.networking.devices.driver_helper import get_snmp_parameters_from_command_context
from cloudshell.networking.snmp_handler_interface import SnmpHandlerInterface
from cloudshell.shell.core.context_utils import get_attribute_by_name

from cloudshell.snmp.quali_snmp import QualiSnmp


class SnmpContextManager(object):
    """
    Context manager to enable/disable snmp
    """

    def __init__(self, enable_flow, disable_flow, snmp_parameters, logger):
        """
        :param enable_flow:
        :param disable_flow:
        :param snmp_parameters:
        :type snmp_parameters:
        :param logger:
        :return:
        """
        self._enable_flow = enable_flow
        self._disable_flow = disable_flow
        self._snmp_parameters = snmp_parameters
        self._logger = logger

    def __enter__(self):
        """
        Execute enable flow and create snmp service
        :return:
        :rtype: QualiSnmp
        """
        if self._enable_flow:
            self._enable_flow.execute_flow(self._snmp_parameters)
        return QualiSnmp(self._snmp_parameters, self._logger)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Disable snmp service
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        if self._disable_flow:
            self._disable_flow.execute_flow()


class SnmpHandler(SnmpHandlerInterface):
    """
    Collect parameters for creating snmp handler
    """

    def __init__(self, context, logger):
        self._context = context
        self._logger = logger
        self._snmp_parameters = get_snmp_parameters_from_command_context(context)

    @property
    def enable_flow(self):
        enable_flow = None
        if get_attribute_by_name(context=self._context, attribute_name='Enable SNMP').lower() == 'true':
            enable_flow = self._create_enable_flow()
        return enable_flow

    @property
    def disable_flow(self):
        disable_flow = None
        if get_attribute_by_name(context=self._context, attribute_name='Disable SNMP').lower() == 'true':
            disable_flow = self._create_disable_flow()
        return disable_flow

    @abstractmethod
    def _create_enable_flow(self):
        pass

    @abstractmethod
    def _create_disable_flow(self):
        pass

    def get_snmp_service(self):
        """
        Enable/Disable snmp
        :param snmp_parameters:
        :return:
        :rtype: SnmpContextManager
        """
        return SnmpContextManager(self.enable_flow, self.disable_flow, self._snmp_parameters, self._logger)
