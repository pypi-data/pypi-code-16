from .host_key_entry import HostKeyEntry
from .file_format import FileFormat

try:
    from .ssh_host_keys_win import SshHostKeys, putty_to_known_host, known_host_to_putty
except ImportError:
    from .ssh_host_keys_nix import SshHostKeys, putty_to_known_host, known_host_to_putty
