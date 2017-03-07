from .base import Command, subparses
import chalk


parser = subparses.add_parser(
    'claim',
    help='claim a JIRA ticket'
)

parser.add_argument(
    '-k',
    '--key',
    help='The issue key to use. Defaults to the name of the active branch.'
)

parser.add_argument(
    '-m',
    '--message',
    help='Add an optional comment to add to the ticket.'
)


class Claim(Command):

    name = 'claim'
    parser = parser

    def run(self, args):
        key = args.key or self.giles.repo.active_branch.name
        key = key.upper()
        issue = self.giles.jira.issue(key)
        self.giles.jira.assign_issue(issue, self.giles.jira.current_user())
        if args.message:
            self.giles.jira.add_comment(issue, args.message)
        return {
            'message': 'Success: Claimed {} '.format(key)
        }
