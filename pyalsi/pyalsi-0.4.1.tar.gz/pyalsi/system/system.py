import os
import math
from datetime import timedelta
from pyalsi.window_managers import window_manager_definitions


class System(object):
    distro = "unknown"
    distro_mappings = dict(Arch='Arch Linux', Apricity='Apricity OS', Ubuntu='Ubuntu')

    def __init__(self):
        self.distro = self.get_distro()
        for sub in System.__subclasses__():
            if self.distro == sub.distro:
                self.__class__ = sub
        self.shell = os.readlink('/proc/%d/exe' % os.getppid())

    @staticmethod
    def get_uptime():
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return str(timedelta(seconds=math.ceil(uptime_seconds)))

    def count_packages(self):
        return self._count_packages()

    def _count_packages(self):
        return 'no data'

    def get_window_manager(self):
        for proc in self.get_processes():
            wm = window_manager_definitions.get(proc)
            if wm:
                return wm

    @staticmethod
    def get_last_login():
        out = os.popen("last $USER -i | grep -E -v 'logged'").read()
        for o in out.splitlines():
            o = o.split()
            if len(o) > 1:
                if not o[-1] == 'in' and not o[0] == 'wtmp':
                    output_dict = {'name': o[0],
                                   'tty': o[1],
                                   'ip': o[2],
                                   'at': '{} {} {} {}:{}'.format(
                                       o[3], o[4], o[5], o[6], o[7].strip(':-'))}
                    return output_dict

    @staticmethod
    def get_processes():
        processes = os.popen('ps -A').read().splitlines()
        processes = [line.split()[3] for line in processes]
        return processes

    def get_distro(self):
        try:
            with open("/etc/issue") as f:
                v = f.read().split()
        except IOError:
            return "Unknown"
        return self.distro_mappings.get(v[0], 'Unknown')

    def get_package_stats(self):
        return {'Pending Updates': self._get_package_stats()}

    def _get_package_stats(self):
        return 'no data'


class ArchLinuxSystem(System):
    distro = 'Arch Linux'

    def _count_packages(self):
        return len([name for name in os.listdir('/var/lib/pacman/local')])

    def _get_package_stats(self):
        pacman_output = os.popen('pacman -Qu').read().splitlines()
        return str(len(pacman_output))


class ApricitySystem(ArchLinuxSystem):
    distro = 'Apricity OS'


class UbuntuSystem(System):
    distro = 'Ubuntu'

    def _count_packages(self):
        for result in os.popen('dpkg -l |grep ^ii | wc -l').read().splitlines():
            if result:
                return result

    def _get_package_stats(self):
        apt_output = os.popen('/usr/lib/update-notifier/apt-check --human-readable').read().splitlines()
        return apt_output[0].split()[0]


class DebianSystem(System):
    distro = 'Debian'
    get_package_stats = UbuntuSystem.get_package_stats


class FedoraSystem(System):
    distro = 'Fedora'

    def count_packages(self):
        return UbuntuSystem.count_packages

