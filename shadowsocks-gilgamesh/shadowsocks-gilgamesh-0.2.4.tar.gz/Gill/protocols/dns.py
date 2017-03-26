import socket,os
from collections import defaultdict


def is_ip(address):
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            if type(address) != str:
                address = address.decode('utf8')
            socket.inet_pton(family, address)
            return family
        except (TypeError, ValueError, OSError, IOError):
            pass
    return False


class  DNSearcher(object):
    """docstring for  DNSearcher"""
    _hosts = defaultdict(lambda : None)

    def __init__(self):

        # super( DNSearcher, self).__init__()

        # self._server = []
        self._parse_host_file()


    def _parse_host_file(self):
        etc_path = '/etc/hosts'
        if 'WINDIR' in os.environ:
            etc_path = os.environ['WINDIR'] + '/system32/drivers/etc/hosts'
        try:
            with open(etc_path, 'rb') as f:
                for line in f.readlines():
                    line = line.strip()
                    parts = line.split()
                    if len(parts) >= 2:
                        ip = parts[0]
                        if is_ip(ip):
                            for i in range(1, len(parts)):
                                hostname = parts[i]
                                if hostname:
                                    self.__setitem__(hostname,ip)
        except IOError:
            self.__setitem__('localhost','127.0.0.1')

    def __setitem__(self, host, ip):
        DNSearcher._hosts.update({host:ip})

    def __getitem__(self, host):
        r = self._hosts[host]
        if r is None:
            try:
                m = socket.gethostbyname(host)
                DNSearcher._hosts.update({host:m})
                return m
            except OSError as e:
                return None
        else:
            return r


