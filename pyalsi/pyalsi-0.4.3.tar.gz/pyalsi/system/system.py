import os
import math
from datetime import timedelta
from pyalsi.window_managers import window_manager_definitions


class System(object):
    distro = "unknown"
    friendly_distro = 'Unknown'
    distro_subclass_map = {}

    def __init__(self):
        self.distro = self.get_distro()
        for sub in System.__subclasses__():
            self.distro_subclass_map[sub.distro] = sub
            if self.distro == sub.distro:
                self.__class__ = sub
            for s in sub.__subclasses__():
                self.distro_subclass_map[s.distro] = s
                if self.distro == s.distro:
                    self.__class__ = s

        self.shell = os.readlink('/proc/%d/exe' % os.getppid())

    def get_distro(self):
        try:
            for line in os.popen("cat /etc/*-release").read().splitlines():
                if line.startswith('NAME='):
                    return line.split('=')[1].strip('"')
        except IOError:
            return "Unknown"

    @staticmethod
    def get_uptime():
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return str(timedelta(seconds=math.ceil(uptime_seconds)))

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

    def get_package_stats(self):
        return {'Pending Updates': self._get_package_stats()}

    def _get_package_stats(self):
        return 'no data'

    def count_packages(self):
        return self._count_packages()

    def _count_packages(self):
        return 'no data'


class ArchLinuxSystem(System):
    distro = 'Arch'
    friendly_distro = 'Arch Linux'

    def _count_packages(self):
        return PackageManager.Pacman.count_packages()

    def _get_package_stats(self):
        return PackageManager.Pacman.get_package_stats()


class ApricitySystem(ArchLinuxSystem):
    distro = 'Apricity OS'
    friendly_distro = 'Apricity OS'


class DebianSystem(System):
    distro = 'Debian'
    friendly_distro = distro

    def _count_packages(self):
        return PackageManager.Dpkg.count_packages()


class UbuntuSystem(DebianSystem):
    distro = 'Ubuntu'
    friendly_distro = distro

    def _get_package_stats(self):
        return PackageManager.Apt.get_package_stats()


class FedoraSystem(System):
    distro = 'Fedora'
    friendly_distro = distro

    def _count_packages(self):
        return PackageManager.Dpkg.count_packages()


class PackageManager(object):
    class Dpkg(object):
        @staticmethod
        def count_packages():
            for result in os.popen('dpkg -l |grep ^ii | wc -l').read().splitlines():
                if result:
                    return result

    class Apt(object):
        @staticmethod
        def get_package_stats():
            apt_output = os.popen('/usr/lib/update-notifier/apt-check --human-readable').read().splitlines()
            return apt_output[0].split()[0]

    class Pacman(object):
        @staticmethod
        def count_packages():
            return len([name for name in os.listdir('/var/lib/pacman/local')])

        @staticmethod
        def get_package_stats():
            pacman_output = os.popen('pacman -Qu').read().splitlines()
            return str(len(pacman_output))
