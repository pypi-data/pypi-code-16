from __future__ import unicode_literals, print_function, absolute_import
from .. import JiraCommand


class Assign(JiraCommand):

    def add_arguments(self):
        self.parser.add_argument(
            'name',
            help='The name of the assignee to use.'
        )

        self.parser.add_argument(
            '-k',
            '--key',
            help='The issue key to use. Defaults to the name of the active branch.'
        )

    def run(self, args):
        key = args.key or self.giles.repo.active_branch.name
        key = key.upper()
        issue = self.giles.jira.issue(key)
        self.giles.jira.assign_issue(issue, args.name)
        return {
            'message': 'Success: Assigned "{}" on {} '.format(args.name, key)
        }
