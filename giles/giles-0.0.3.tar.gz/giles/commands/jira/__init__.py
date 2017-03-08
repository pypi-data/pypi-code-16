from __future__ import unicode_literals, print_function, absolute_import
from giles.commands.bases import CommandBase, SubCommandBase
from giles.commands.giles import Giles
# http://jira.readthedocs.io/en/latest/api.html#jira.JIRA.search_assignable_users_for_issues


class Jira(CommandBase):
    giles = Giles(configure=True)


class JiraCommand(SubCommandBase):

    parent = Jira
    abstract = True

    @property
    def giles(self):
        return self.parent.giles