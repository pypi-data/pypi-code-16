from __future__ import unicode_literals, print_function

__version__ = "0.0.0"

# http://gitpython.readthedocs.io/en/stable/
# http://jira.readthedocs.io/en/latest
# http://pygithub.readthedocs.io/en/latest/introduction.html
try:
    import ConfigParser as configparser
except ImportError:  # pragma: no cover
    import configparser

# installed libraries
try:
    from . import parsers, utils, commands
    from github import Github
    from jira import JIRA

    import git
except ImportError as err:
    pass


class Giles(object):

    _commands = ['setup', 'jira', 'transition', 'assign', 'branch', 'submit']
    additional_commands = []

    def __init__(self):
        self.rc_name = '.gilesrc'
        self.profile_name = '.gilesrc_profile'
        self.config = configparser.SafeConfigParser()
        self.profile = configparser.SafeConfigParser()
        self._setup()

    def _configure(self):
        self.config.read('.gilesrc')
        self.profile.read('.gilesrc_profile')


        self.jira = JIRA(
            self.config.get('jira', 'url'),
            basic_auth=(
                self.profile.get('jira', 'username'),
                self.profile.get('jira', 'password')
            )
        )

        self.default_branch = self.config.get('github', 'branch')
        self.project = self.config.get('github', 'project')
        self.repo = git.Repo(self.config.get('github', 'repo_path'))
        self.git = self.repo.git

        self.github = Github(
            self.profile.get('github', 'username'),
            self.profile.get('github', 'password')
        )

    @property
    def commands(self):
        return self._commands + self.additional_commands

    def add_subcommand(self, name):
        if name in commands.registry and name not in self.commands:
            self.additional_commands.append(name)
            cls = commands.registry.get(name)
            cls(self)

    def _setup(self):
        for name in self.commands:
            cls = commands.registry.get(name)
            cls(self)

    def run(self):
        args = parsers.main.parse_args()
        args.func(args)
