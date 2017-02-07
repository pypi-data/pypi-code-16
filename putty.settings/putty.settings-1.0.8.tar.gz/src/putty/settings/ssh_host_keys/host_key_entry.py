import logging
import re
import typing
import paramiko
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa


logger = logging.getLevelName(__name__)


paramiko_to_putty_key = {
    "ssh-rsa": "rsa2"
}

putty_to_paramiko_key = {val: key for key, val in paramiko_to_putty_key.items()}


class HostKeyEntry:

    putty_host_entry_pattern = re.compile(r'(?P<key_type>.+)@(?P<port>.+):(?P<hostname>.+)')
    paramiko_host_entry_pattern = re.compile(r'\[(?P<hostname>.+)\]:(?P<port>.+)')

    def __init__(self, hostname: str = None, port: str = None, key_type: str = None, key: paramiko.PKey = None):
        self.hostname = hostname
        self.port = port
        self.key_type = key_type
        self.key = key

    @property
    def paramiko_host_entry(self):
        if self.port == '22':
            return self.hostname
        else:
            return "[{hostname}]:{port}".format(hostname=self.hostname, port=self.port)

    @paramiko_host_entry.setter
    def paramiko_host_entry(self, value):
        m = self.paramiko_host_entry_pattern.match(value)
        if m:
            self.hostname = m.group('hostname')
            self.port = m.group('port')
        else:
            self.hostname = value
            self.port = '22'

    @property
    def paramiko_key_type(self):
        return self.key_type

    @paramiko_key_type.setter
    def paramiko_key_type(self, value):
        self.key_type = value

    @property
    def paramiko_key(self):
        return self.key

    @paramiko_key.setter
    def paramiko_key(self, value):
        self.key = value

    @property
    def putty_key_type(self):
        return paramiko_to_putty_key[self.key_type]

    @putty_key_type.setter
    def putty_key_type(self, value):
        self.key_type = putty_to_paramiko_key[value]

    @property
    def putty_host_entry(self):
        return "{key_type}@{port}:{hostname}".format(key_type=self.putty_key_type, port=self.port, hostname=self.hostname)

    @putty_host_entry.setter
    def putty_host_entry(self, value):
        m = self.putty_host_entry_pattern.match(value)
        if m:
            self.hostname = m.group('hostname')
            self.port = m.group('port')
            self.putty_key_type = m.group('key_type')
        else:
            raise Exception("Not valid host_entry")

    @property
    def putty_key(self):
        if self.key_type == 'ssh-rsa' and isinstance(self.key, paramiko.RSAKey):
            return '{e},{n}'.format(e=hex(self.key.public_numbers.e), n=hex(self.key.public_numbers.n))

    @putty_key.setter
    def putty_key(self, value):
        if self.key_type == 'ssh-rsa':
            e, n = (int(x, 0) for x in value.split(','))
            self.key = paramiko.RSAKey(key=rsa.RSAPublicNumbers(e=e, n=n).public_key(default_backend()))

    @classmethod
    def from_registry_entry(cls, entry: typing.Tuple[str, str, int]):
        o = cls()
        o.putty_host_entry = entry[0]
        o.putty_key = entry[1]
        return o

    @classmethod
    def from_paramiko_entry(cls, host_entry, key_type, key):
        o = cls()
        o.paramiko_host_entry = host_entry
        o.paramiko_key_type = key_type
        o.paramiko_key = key
        return o