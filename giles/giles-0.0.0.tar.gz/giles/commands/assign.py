from .base import Command, subparses
import chalk


parser = subparses.add_parser(
    'assign',
    help='Assign a JIRA ticket'
)

parser.add_argument(
    'name',
    help='The name of the assignee to use.'
)

parser.add_argument(
    '-k',
    '--key',
    help='The issue key to use. Defaults to the name of the active branch.'
)


class Assign(Command):

    name = 'assign'
    parser = parser

    def run(self, args):
        key = args.key or self.giles.repo.active_branch.name
        key = key.upper()
        issue = self.giles.jira.issue(key)
        self.giles.jira.assign_issue(issue, args.name)
        return {
            'message': 'Success: Assigned "{}" on {} '.format(args.name, key)
        }
