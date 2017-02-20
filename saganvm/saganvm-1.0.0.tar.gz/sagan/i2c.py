from abc import abstractmethod
import struct


class I2cDevice:
    """
    A light wrapper on top of smbus for convenience.
    """
    def __init__(self, bus, address):
        self.bus = bus
        self.address = address

    def read(self, cmd, length):
        return

    def write(self, cmd, values):
        return

    def read_and_unpack(self, cmd, fmt):
        return

    def pack_and_write(self, cmd, fmt, values):
        return

    @abstractmethod
    def configure(self, args):
        pass

    @abstractmethod
    def self_test(self):
        pass

    def __repr__(self):
        return ""
