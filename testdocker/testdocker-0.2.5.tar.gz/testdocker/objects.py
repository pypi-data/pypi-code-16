"""
testdocker.objects
~~~~~~~~~~~~~~

Classes for interacting with docker-compose and docker.

:copyright: (c) 2016 by Joe Black.
:license: Apache2.
"""

import os
import time
import re
import subprocess
import docker

from . import util


COMPOSE_DEFAULT_FILES = ('docker-compose.yml', 'docker-compose.yaml')


class Compose:
    defaults = dict(
        globals=dict(
            options=dict(
                files=COMPOSE_DEFAULT_FILES
            ),
            flags=[],
        ),
        up=['daemonize', 'no_build'],
        down=['volumes']
    )

    def __init__(self, options=None, flags=None):
        self.options = util.set_defaults(
            options or {}, self.defaults['globals']['options'])
        self.flags = util.set_defaults(
            flags or [], self.defaults['globals']['flags'])
        self._discover_compose_files()

    def _discover_compose_files(self):
        self.options['files'] = [file for file in
                                 util.filter_dupes(self.options['files'])
                                 if os.path.exists(file)]

    def _build_global_args(self):
        args = []
        for key in self.options:
            if key == 'files':
                files = self.options[key]
                args.extend(['--file {}'.format(file) for file in files])
            elif key == 'project_name':
                args.append('--project-name {}'.format(self.options[key]))
        for flag in self.flags:
            args.append(util.format_flag(flag))
        return args

    def _build_command_args(self, command, flags=None):
        flags = util.set_defaults(flags or [], self.defaults[command])
        args = []
        if command == 'up':
            for flag in flags:
                if flag == 'daemonize':
                    args.append('-d')
                else:
                    args.append(util.format_flag(flag))
        elif command == 'down':
            for flag in flags:
                args.append(util.format_flag(flag))
        return list(util.filter_dupes(args))

    def _build_args_for(self, command, flags=None):
        flags = flags or []
        args = {}
        args['globals'] = self._build_global_args()
        args[command] = self._build_command_args(command, flags)
        return args

    def _build_command(self, command, args):
        return 'docker-compose {} {} {}'.format(
            ' '.join(args['globals']), command, ' '.join(args[command])
        )

    def up(self, options=None, flags=None):
        args = self._build_args_for('up', flags)
        exit_code, output = self.execute('up', args)
        if exit_code != 0:
            raise Exception(output)
        print_results('up', output)
        return self._parse_containers(output)

    def down(self, options=None, flags=None):
        args = self._build_args_for('down', flags)
        return self.execute('down', args, test_success=True)

    def execute(self, command, args=None, test_success=False):
        command = self._build_command(command, args)
        return self.shell(command, test_success)

    @staticmethod
    def shell(command, test_success=False):
        exit_code, output = subprocess.getstatusoutput(command)
        if test_success:
            return exit_code == 0
        return exit_code, output

    @staticmethod
    def _parse_containers(output):
        names = extract_container_names(output)
        return [Container(name) for name in names]


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


def print_results(command, output):
    print('\nContainers {}:\n{}\n'.format(command, output.strip()))

def extract_container_names(output):
    pattern = re.compile(
        r'^(?:Creating )?(.+?)(?:is up-to-date)?$', re.MULTILINE)
    filtered = util.filter_lines(output, r'^Creating network')
    return [match.group(1).strip() for match in pattern.finditer(filtered)]


# container = Container('kazoo')
# compose = Compose(options=dict(files=['docker-compose.yaml']))
