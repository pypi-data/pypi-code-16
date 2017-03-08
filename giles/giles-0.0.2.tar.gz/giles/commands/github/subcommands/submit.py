from __future__ import unicode_literals, print_function, absolute_import
from .. import GitHubCommand


class Submit(GitHubCommand):

    def add_arguments(self):
        self.parser.add_argument(
            'title',
            help='The title to use for the pull request.'
        )

        self.parser.add_argument(
            '--head',
            default=None,
            help=(
                'Name of the branch, commit or tag that you want to use in the PR. '
                'Note that this is the "from" branch e.g. PR from MYBRANCH to master'
            )
        )

        self.parser.add_argument(
            '-b',
            '--base',
            help=(
                'Base is the branch you are submitting the PR to. Defaults to the '
                'name of the default branch.'
            )
        )


        self.parser.add_argument(
            '-m',
            '--message',
            help='Optional message to include in your PR.'
        )

    def run(self, args):
        head = args.head or self.giles.repo.active_branch.name
        base = args.base or self.giles.default_branch
        repo = self.giles.github.get_repo(self.giles.project)
        response = repo.create_pull(
            title=args.title,
            body=args.message or '',
            base=base,
            head=head,
        )
        return {
            'message': 'Success: Created PR#{} from "{}" to "{}"'.format(
                response.number, head, base
            )
        }
