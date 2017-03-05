import psutil
from pyalsi.utils import types


class Ram(object):
    def __init__(self):
        self.percent = None
        self.total = None
        self.used = None
        self.__dict__.update(psutil.virtual_memory().__dict__)

    def get_total(self):
        return types.Bytes(self.total)

    def get_used(self):
        return types.Bytes(self.used)
