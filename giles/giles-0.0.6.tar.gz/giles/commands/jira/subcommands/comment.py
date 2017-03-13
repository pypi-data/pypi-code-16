from __future__ import unicode_literals, print_function, absolute_import
from .. import JiraCommand


class Comment(JiraCommand):
    """
    Comment an issue to someone
    """

    def add_arguments(self):
        self.parser.add_argument(
            'body',
            help='The comment content.'
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
        self.giles.jira.add_comment(issue, args.body)
        return {
            'message': 'Success: Added comment on {} '.format(key)
        }
