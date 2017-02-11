"""
testdocker.objects
~~~~~~~~~~~~~~

Classes for interacting with docker-compose and docker.

:copyright: (c) 2016 by Joe Black.
:license: Apache2.
"""


import time
import subprocess
import docker

from . import util


class Compose:
    defaults = dict(
        up=dict(
            daemonize=True
        ),
        down=dict(
            volumes=True
        )
    )

    @classmethod
    def up(cls, options=None):
        options = util.set_defaults(options or {}, cls.defaults['up'])
        cls.execute('up', options)

    @classmethod
    def down(cls, options=None):
        options = util.set_defaults(options or {}, cls.defaults['down'])
        cls.execute('down', options)

    @staticmethod
    def _build_args(command, options):
        args = []
        if command == 'up':
            if options.get('daemonize'):
                args.append('-d')
        elif command == 'down':
            if options.get('volumes'):
                args.append('-v')
        return ' '.join(args)

    @classmethod
    def execute(cls, command, options):
        args = cls._build_args(command, options)
        cls.shell('docker-compose %s %s' % (command, args))

    @staticmethod
    def shell(command, return_code=False):
        code, output = subprocess.getstatusoutput(command)
        if return_code:
            return code == 0
        return output


class Container:
    def __init__(self, name, client=None, delay=8):
        self.client = client or docker.from_env()
        self.name = name
        self.delay = delay
        self.obj = self.client.containers.get(name)

    def __repr__(self):
        return '%s(%s)' % (
            type(self).__name__,
            self.name
        )

    @property
    def network(self):
        network = self.inspect['HostConfig']['NetworkMode']
        return self.inspect['NetworkSettings']['Networks'][network]

    @property
    def ip(self):
        return self.network['IPAddress']

    @property
    def hostnames(self):
        return self.network['Aliases']

    @property
    def env(self):
        return dict(
            [item.split('=') for item in self.inspect['Config']['Env']])

    @property
    def inspect(self):
        return self.obj.attrs

    def reload(self):
        self.obj.reload()

    @property
    def health(self):
        return self.obj.attrs['State']['Health']['Status']

    @property
    def is_healthy(self):
        return self.health == 'healthy'

    def wait(self):
        while not self.is_healthy:
            time.sleep(self.delay)
            self.reload()

    @property
    def logs(self):
        return self.obj.logs().decode().strip()

    def exec(self, cmd, test_success=False, output_only=False,
             exit_code_only=False):
        if not isinstance(cmd, str):
            cmd = str(cmd)
        exec_id = self.client.api.exec_create(self.name, cmd).get('Id')
        output = self.client.api.exec_start(exec_id).decode().strip()
        exit_code = self.client.api.exec_inspect(exec_id).get('ExitCode')
        if test_success:
            return exit_code == 0
        if output_only:
            return output
        if exit_code_only:
            return exit_code
        return exit_code, output


# container = Container('kazoo')
