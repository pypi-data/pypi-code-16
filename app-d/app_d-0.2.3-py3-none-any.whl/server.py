from getpass import getpass
from os.path import expanduser
from paramiko import SSHConfig, SSHClient, AutoAddPolicy


class Server:
    "Wrapper for a remote server"

    def __init__(self, hostname):
        self.hostname = hostname
        ssh_config = SSHConfig()
        ssh_config.parse(open(expanduser('~/.ssh/config')))
        self.info = ssh_config.lookup(self.hostname)
        try:
            self.user = self.info['user']
        except KeyError:
            raise KeyError('Your SSH Config is missing! Ensure an entry is present for {} in ~/.ssh.config'.format(self.hostname))
        self._client = None
        self.password = getpass('Server user password: ')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.connection.close()
        self._client = None

    @property
    def connection(self):
        if self._client:
            return self._client
        self._client = SSHClient()
        # Important! This is vulnerable to MITM attacks, but unfortunately the
        # only way to deal with ECDSA keys until paramiko is patched
        # See https://github.com/paramiko/paramiko/pull/473
        self._client.set_missing_host_key_policy(AutoAddPolicy())
        self._client.connect(self.info['hostname'], username=self.info['user'], password=self.password or None, key_filename=self.info.get('identityfile'))
        return self._client

    def run(self, command, include_input=None):
        stdin, stdout, stderr = self.connection.exec_command(command)
        if include_input:
            stdin.write(include_input)
            stdin.flush()
        # Abort on errors
        errors = stderr.readlines()
        if errors:
            raise Exception('\n'.join(errors))
        return '\n'.join(stdout.readlines())

    def sudo(self, command):
        return self.run('sudo -S -p "" {}'.format(command), '{}\n'.format(self.password))
