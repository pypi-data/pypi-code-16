from __future__ import unicode_literals, print_function, absolute_import
# http://gitpython.readthedocs.io/en/stable/
# http://jira.readthedocs.io/en/latest
# http://pygithub.readthedocs.io/en/latest/introduction.html
try:
    import ConfigParser as configparser
except ImportError:  # pragma: no cover
    import configparser

from giles.commands.bases import CommandBase, SubCommandBase
from github import Github
from jira import JIRA
import git
import os

RC = os.environ.get('GILESRC', '.gilesrc')
PROFILE = os.environ.get('GILESRCPROFILE', '.gilesrc_profile')


class Giles(CommandBase):
    """
        Giles is a terminal based workflow manager that integrates JIRA with
        both slack and github.
    """
    _is_configured = False
    _is_setup = False

    def __init__(self, configure=False):
        if configure:
            self._configure()

    def _configure(self):
        if not self._is_configured:
            self.config = configparser.SafeConfigParser()
            self.profile = configparser.SafeConfigParser()

            if os.path.isfile(RC) and os.path.isfile(PROFILE):
                self._is_setup = True

            if self._is_setup:
                self.config.read(RC)
                self.profile.read(PROFILE)

                self.default_branch = self.config.get('github', 'branch')
                self.project = self.config.get('github', 'project')
                self.repo = git.Repo(self.config.get('github', 'repo_path'))
                self.git = self.repo.git
                self._is_configured = True

    @property
    def github(self):
        if not hasattr(self, '_github'):
            self._github = Github(
                self.profile.get('github', 'username'),
                self.profile.get('github', 'password')
            )
        return self._github

    @property
    def jira(self):
        if not hasattr(self, '_jira'):
            self._jira = JIRA(
                self.config.get('jira', 'url'),
                basic_auth=(
                    self.profile.get('jira', 'username'),
                    self.profile.get('jira', 'password')
                )
            )
        return self._jira

class GilesCommand(SubCommandBase):
    abstract = True
    parent = Giles
