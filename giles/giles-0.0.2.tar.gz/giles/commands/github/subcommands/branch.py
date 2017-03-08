from __future__ import unicode_literals, print_function, absolute_import
from .. import GitHubCommand


class Branch(GitHubCommand):

    def add_arguments(self):
        self.parser.add_argument(
            'name',
            help='The name of the branch to use.'
        )

        self.parser.add_argument(
            '-c',
            '--checkout',
            help='The branch to checkout. Defaults to the name of the default branch.'
        )

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
