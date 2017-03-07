from .base import Command, subparses
import chalk


parser = subparses.add_parser(
    'branch',
    help=(
        'Shortcut for checkout, fetching and creating a new branch with the '
        'specified name.'
    )
)

parser.add_argument(
    'name',
    help='The name of the branch to use.'
)

parser.add_argument(
    '-c',
    '--checkout',
    help='The branch to checkout. Defaults to the name of the default branch.'
)


class Branch(Command):

    name = 'branch'
    parser = parser

    def run(self, args):
        checkout_branch = args.checkout or self.giles.default_branch
        self.giles.git.checkout(checkout_branch)
        self.giles.git.fetch()
        self.giles.git.checkout('-b', args.name)

        return {
            'message': 'Success: Created branch "{}" from "{}"'.format(
                args.name, checkout_branch
            )
        }
