from cpuinfo import cpuinfo


class Cpu(object):
    def __init__(self):
        self.count = None
        self.brand = None
        self.__dict__.update(cpuinfo.get_cpu_info_from_proc_cpuinfo())

    def to_info_string(self):
        fmt = "{} cores" if self.count > 1 else "{} core"
        return "{} ({})".format(self.brand, fmt.format(self.count))
