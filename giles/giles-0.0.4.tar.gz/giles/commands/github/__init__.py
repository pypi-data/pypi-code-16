from __future__ import unicode_literals, print_function, absolute_import
from giles.commands.bases import CommandBase, SubCommandBase
from giles.commands.giles import Giles


class GitHub(CommandBase):
    giles = Giles(configure=True)


class GitHubCommand(SubCommandBase):
    parent = GitHub
    abstract = True

    @property
    def giles(self):
        return self.parent.giles