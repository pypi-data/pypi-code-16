from abc import ABCMeta
from abc import abstractmethod


class AutoloadOperationsInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def discover(self):
        pass

    @abstractmethod
    def enable_snmp(self):
        pass

    @abstractmethod
    def disable_snmp(self):
        pass
