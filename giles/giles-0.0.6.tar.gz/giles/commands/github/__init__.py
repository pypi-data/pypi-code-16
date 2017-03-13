from __future__ import unicode_literals, print_function, absolute_import
from giles.commands.bases import CommandBase, SubCommandBase
from giles.commands.giles import Giles

import chalk
import requests


class GitHub(CommandBase):
    giles = Giles(configure=True)


class GitHubCommand(SubCommandBase):
    parent = GitHub
    abstract = True

    @property
    def giles(self):
        return self.parent.giles

    @property
    def repo(self):
        if not hasattr(self, '_repo'):
            self._repo = self.giles.github.get_repo(self.giles.project)
        return self._repo

    @property
    def git(self):
        if not hasattr(self, '_git'):
            self._git = self.giles.git
        return self._git

    @property
    def client(self):
        if not hasattr(self, '_client'):
            username = self.giles.profile.get('github', 'username')
            password = self.giles.profile.get('github', 'password')
            self._client = requests.Session()
            self._client.auth = requests.auth.HTTPBasicAuth(username, password)
            self._client.headers.update({
                'Accept': 'application/vnd.github.black-cat-preview+json'
            })
        return self._client

    def format_diff(self, diff):
        lines = diff.split('\n')

        for idx, line in enumerate(lines):
            startswith =line.startswith
            if startswith('@@') or startswith('diff') or startswith('index'):
                lines[idx] = chalk.format_txt('white', line, None, ['bold'])
            elif startswith('-'):
                lines[idx] = chalk.format_txt(
                    'red',
                    line,
                    None,
                    ['bold']
                )
            elif startswith('+'):
                lines[idx] = chalk.format_txt(
                    'green',
                    line,
                    None,
                    ['bold']
                )

        return '\n'.join(lines)

    def checkout_remote(self, path, silent=False):
        remote, branch_name = path.split('/')
        if not self.git.branch('--list', branch_name):
            self.git.checkout('-t', path)
        elif not silent:
            raise RuntimeError('Branch {} already exists'.format(branch_name))
