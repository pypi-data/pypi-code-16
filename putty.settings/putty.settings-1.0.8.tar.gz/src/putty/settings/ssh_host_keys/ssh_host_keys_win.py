import paramiko
import winreg
import pathlib
import typing
import logging

from .file_format import FileFormat
from .host_key_entry import HostKeyEntry

logger = logging.getLevelName(__name__)

STORE = winreg.HKEY_CURRENT_USER
PUTTY_PATH = pathlib.PureWindowsPath('Software', 'SimonTatham', 'PuTTY')


def putty_to_known_host(filename: pathlib.Path = pathlib.Path.home().joinpath('.ssh', 'known_hosts')):
    ssh_host_keys = SshHostKeys()
    ssh_host_keys.load_from_registry()
    ssh_host_keys.save_to_file(filename)


def known_host_to_putty(filename: pathlib.Path = pathlib.Path.home().joinpath('.ssh', 'known_hosts')):
    ssh_host_keys = SshHostKeys()
    ssh_host_keys.load_from_file(filename)
    ssh_host_keys.save_to_registry()


class SshHostKeys:

    path = str(PUTTY_PATH.joinpath('SshHostKeys'))

    def __init__(self):
        self.host_keys: typing.Dict[str, HostKeyEntry] = {}

    def clear(self):
        self.host_keys.clear()

    def load_from_registry(self):
        for registry_entry in self.get_from_registry():
            try:
                self.add(HostKeyEntry.from_registry_entry(registry_entry))
            except Exception:
                logger.info("Invalid keyformat {}".format(registry_entry))

    def save_to_registry(self):
        entries_to_remove = []
        for registry_entry in self.get_from_registry():
            if self.host_keys.get(registry_entry[0]) is None:
                entries_to_remove.append(registry_entry[0])
        self.delete_from_registry(entries_to_remove)

        self.set_registry_to(self.host_keys)

    def save_to_file(self, filename: pathlib.Path, save_type: FileFormat = FileFormat.known_hosts):
        if save_type == FileFormat.known_hosts:
            host_keys = paramiko.HostKeys()
            self.add_to_paramiko_host_keys(host_keys)
            host_keys.save(str(filename))

    def load_from_file(self, filename: pathlib.Path, load_type: FileFormat = FileFormat.known_hosts):
        if load_type == FileFormat.known_hosts:
            host_keys = paramiko.HostKeys(str(filename))
            self.add_from_paramiko_host_keys(host_keys)

    def add(self, host_key_entry: HostKeyEntry):
        self.host_keys[host_key_entry.putty_host_entry] = host_key_entry

    def add_from_paramiko_host_keys(self, host_keys: paramiko.HostKeys):
        for host_entry in host_keys.keys():
            for key_type, key in host_keys.lookup(host_entry).items():
                self.add(HostKeyEntry.from_paramiko_entry(host_entry=host_entry, key_type=key_type, key=key))

    def add_to_paramiko_host_keys(self, host_keys: paramiko.HostKeys):
        for key_type, host_key in self.host_keys.items():
            host_keys.add(hostname=host_key.paramiko_host_entry, keytype=host_key.paramiko_key_type, key=host_key.paramiko_key)

    @classmethod
    def delete_from_registry(cls, entries):
        with winreg.OpenKey(STORE, cls.path, 0, winreg.KEY_ALL_ACCESS) as key:
            for entry in entries:
                winreg.DeleteValue(key, entry)

    @classmethod
    def get_from_registry(cls):
        with winreg.OpenKey(STORE, cls.path, 0, winreg.KEY_ALL_ACCESS) as key:
            size = winreg.QueryInfoKey(key)[1]
            return [winreg.EnumValue(key, i) for i in range(size)]

    @classmethod
    def set_registry_to(cls, host_keys):
        with winreg.OpenKey(STORE, cls.path, 0, winreg.KEY_ALL_ACCESS) as key:
            for key_type, host_key in host_keys.items():
                try:
                    winreg.SetValueEx(key, host_key.putty_host_entry, 0, 1, host_key.putty_key)
                except Exception:
                    logger.info("Invalid keyformat {}".format(host_key))
