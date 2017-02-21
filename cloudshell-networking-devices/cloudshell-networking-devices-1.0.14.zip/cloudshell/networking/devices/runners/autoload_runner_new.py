#!/usr/bin/python
# -*- coding: utf-8 -*-
from abc import abstractmethod, ABCMeta

from cloudshell.networking.devices.flows.snmp_action_flows import AutoloadFlow
from cloudshell.shell.core.context_utils import get_resource_name


class AutoloadRunner(object):
    __metaclass__ = ABCMeta

    def __init__(self, context, supported_os):
        """
        Facilitate SNMP autoload,
        :param supported_os:
        :param context:
        :param Cli cli:
        :param QualiSnmp snmp_handler:
        """
        self._context = context
        self._supported_os = supported_os
        self._resource_name = get_resource_name(self._context)

    @property
    def autoload_flow(self):
        """
        Autoload flow property
        :return:
        :rtype: AutoloadFlow
        """
        return self.create_autoload_flow()

    @abstractmethod
    def create_autoload_flow(self):
        pass

    def discover(self):
        """Enable and Disable SNMP communityon the device, Read it's structure and attributes: chassis, modules,
        submodules, ports, port-channels and power supplies

        :return: AutoLoadDetails object
        """
        return self.autoload_flow.execute_flow(self._supported_os, self._resource_name)
