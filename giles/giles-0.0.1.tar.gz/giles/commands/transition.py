from .base import Command, subparses
import chalk


parser = subparses.add_parser(
    'transition',
    help='transition a JIRA ticket'
)

parser.add_argument(
    'name',
    help='The name of the transition to use.'
)

parser.add_argument(
    '-k',
    '--key',
    help='The issue key to use. Defaults to the name of the active branch.'
)


class Transition(Command):

    name = 'transition'
    parser = parser

    def run(self, args):
        key = args.key or self.giles.repo.active_branch.name
        key = key.upper()
        issue = self.giles.jira.issue(key)
        self.giles.jira.transition_issue(issue, args.name)
        return {
            'message': 'Success: "{}" on {} '.format(args.name, key)
        }
