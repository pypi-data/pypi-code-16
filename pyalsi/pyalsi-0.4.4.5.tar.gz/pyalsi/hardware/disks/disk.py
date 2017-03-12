import psutil

from pyalsi.utils.types import Bytes
from pyalsi.utils.strings import colorize_usage, colorize_percent, Colors


class Disk(object):
    def __init__(self, disk):
        name = disk.mountpoint.split('/')[-1]
        self.usage = self.Usage(psutil.disk_usage(disk.mountpoint))
        self.name = name.capitalize() if name != "" else "Root"  # Type: str
        self.fstype = disk.fstype

    def to_info_string(self):
        return ("{c2}{}: {} ({}) ({})".format(
            self.name,
            colorize_usage(self.usage.used.to_gigabytes(),
                           self.usage.total.to_gigabytes(),
                           self.usage.percent, "G"),
            colorize_percent(self.usage.percent, "%"),
            self.fstype, **Colors.colors))

    class Usage(object):
        def __init__(self, usage):
            self.used = Bytes(usage.used)
            self.total = Bytes(usage.total)
            self.percent = int(usage.percent)


class DiskGroup(object):
    def __init__(self):
        self.disks = [Disk(disk) for disk in psutil.disk_partitions()]
