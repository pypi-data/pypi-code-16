import json
from os import mkdir
from os.path import isfile, isdir

from serapeum.backup import config

from serapeum.backup.modules.run import Run


class RdiffRole:
    def __init__(self, remote_role, sources, destination_path, remote_user, remote_host, ssh_key, excludes=None,
                 delete_older_than=None, sources_is_file=True, excludes_is_file=True):
        self.c = config
        self.__remote_role = remote_role
        self.__destination_path = destination_path
        self.__remote_user = remote_user
        self.__remote_host = remote_host
        if sources_is_file:
            self.sources = self.__parse_sources_file(sources)
        else:
            self.sources = sources
        if excludes and excludes_is_file:
            self.excludes = self.__parse_sources_file(excludes)
        elif excludes:
            self.excludes = excludes
        else:
            self.excludes = []
        self.ssh_key = ssh_key
        self.delete_older_than = delete_older_than
        self.__cmd_output = ''

    @property
    def cmd_output(self):
        return self.__cmd_output

    @cmd_output.setter
    def cmd_output(self, command_output):
        self.__cmd_output += command_output

    @property
    def destination(self):
        if self.__remote_role == 'source':
            self.create_local_destination()
            return self.__destination_path
        elif self.__remote_role == 'backup':
            self.create_remote_destination()
            return '{user}@{host}::{path}'.format(user=self.__remote_user, host=self.__remote_host,
                                                  path=self.__destination_path)
        else:
            raise Exception('Illegal remote_role specified!')

    @property
    def source(self):
        if self.__remote_role == 'source':
            return '{user}@{host}::/'.format(user=self.__remote_user, host=self.__remote_host)
        elif self.__remote_role == 'backup':
            return '/'
        else:
            raise Exception('Illegal remote_role specified!')

    @property
    def command(self):
        """
            Build the command we will make rdiff-backup run
            :return:
            """
        command = [
            self.c.config['SYSTEM']['rdiff_path'],
            '-v0',
            '--print-statistics',
            '--exclude-special-files',
            '--remote-schema',
            '/usr/bin/ssh -i "{ssh_key}" -C %s "sudo /usr/bin/rdiff-backup --server"'
                .format(ssh_key=self.ssh_key)
        ]
        for d in self.excludes:
            command += ['--exclude', d]
        for d in self.sources:
            command += ['--include', d]
        command += [
            '--exclude',
            '**',
            self.source,
            self.destination
        ]
        return command

    def __parse_sources_file(self, filename):
        dir_list = []
        if not isfile(filename):
            raise Exception('Failed to read directory list from {0}: file not found.'.format(filename))
        with open(filename, 'r') as f:
            try:
                sources_parsed = json.load(f)
                dir_list = sources_parsed['list']
            except json.JSONDecodeError:
                raise Exception('Failed to read directory list from {0}: syntax error.'.format(filename))
            except KeyError:
                raise Exception('Invalid sources file!')
        return dir_list

    def __run(self, command):
        r = Run()
        try:
            r.run(command)
        except Exception as e:
            self.cmd_output = r.cmd_output
            raise e
        return r.cmd_output

    def __delete_older(self, delete_older_than):
        command = [
            self.c.config['SYSTEM']['rdiff_path'],
            '-v0',
            '--print-statistics',
            '--remove-older-than',
            delete_older_than
        ]
        if self.__remote_role == 'backup':
            command += [
                '--remote-schema',
                '/usr/bin/ssh -i "{ssh_key}" -C %s "sudo /usr/bin/rdiff-backup --server"'
                    .format(ssh_key=self.ssh_key)
            ]

        command += [
            self.destination
        ]
        return self.__run(command)

    def create_remote_destination(self):
        command = [
            '/usr/bin/ssh',
            '-i',
            self.ssh_key,
            '{user}@{host}'.format(user=self.__remote_user, host=self.__remote_host),
            '/bin/mkdir -p "{path}"'.format(path=self.__destination_path)
        ]
        self.__run(command)

    def create_local_destination(self):
        if not isdir(self.__destination_path):
            mkdir(self.__destination_path)

    def run(self):
        self.__run(self.command)
        if self.delete_older_than is not None:
            # Delete older increments
            self.__delete_older(self.delete_older_than)
        return True
