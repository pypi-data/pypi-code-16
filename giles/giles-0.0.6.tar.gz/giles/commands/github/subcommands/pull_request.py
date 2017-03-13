from __future__ import unicode_literals, print_function, absolute_import
from .. import GitHubCommand
from giles.utils import get_input

import chalk


class PullRequestBase(GitHubCommand):
    """
    Pull request review interface
        https://developer.github.com/v3/pulls/reviews/
    """
    abstract = True
    _continue = True

    def add_base_arguments(self):
        self.parser.add_argument(
            'number',
            type=int,
            nargs='?',
            default=None,
            help='Pull request number'
        )
        self.parser.add_argument(
            '--fetch',
            help='fetch all before running anything',
            action='store_true'
        )
        self.parser.add_argument(
            '--details',
            help='details of the pull request',
            action='store_true'
        )
        self.parser.add_argument(
            '--diff',
            help='print out the diff',
            action='store_true'
        )
        self.parser.add_argument(
            '-q',
            '--quiet',
            help='silence listing of reviews',
            action='store_true'
        )
        self.parser.add_argument(
            '-m',
            dest='comment',
            help='add a comment to the pull request'
        )

    def base_run(self, args):
        if args.fetch:
            self.git.fetch('--all')

        if args.number is None:
            self._continue = False
            return {'table': self.parent.list.render_pull_requests()}

        self.pr = self.repo.get_pull(args.number)

        if args.details:
            self._continue = False
            return self.format_details()
        if args.diff:
            self._continue = False
            return self.print_diff()

    def reviews(self):
        resp = self.client.get(self.pr.url + '/reviews')
        resp.raise_for_status()
        return resp.json()

    def format_reviews(self):
        reviews = self.reviews()
        return {
            'table': {
                'heading': ['ID', 'STATE', 'USER'],
                'data': [
                    (review['id'], review['state'], review['user']['login'])
                    for review in reviews
                ]
            }
        }

    def format_details(self):
        return {
            'table': {
                'heading': [
                    '{} PR: {}  by {} | {} -> {}'.format(
                        self.pr.state.upper(),
                        self.pr.number,
                        self.pr.user.login,
                        self.pr.head.ref,
                        self.pr.base.ref,
                    )
                ],
                'data': [
                    (self.pr.html_url + '/files\n',),
                    (
                        'COMMENTS: {}'.format(self.pr.comments),
                        'REVIEWS: {}'.format(len(self.reviews()))
                    ),
                    ('TITLE:',),
                    ('', self.pr.title,),
                    ('BODY:',),
                    ('', self.pr.body,)
                ],
                'width': 6
            },
        }

    def checkout_remotes(self):
        _branch_name = self.giles.repo.active_branch.name
        self.checkout_remote('origin/' + self.pr.head.ref, silent=True)
        self.checkout_remote('origin/' + self.pr.base.ref, silent=True)
        self.git.checkout(_branch_name)

    def print_diff(self):
        self.checkout_remotes()
        diff = self.git.diff(self.pr.base.sha, self.pr.head.sha)
        if not diff:
            return

        sep = 'diff --'
        files = diff[6:].split(sep)
        chalk.magenta(
            '######\n\nHit Enter for the next file\n\n######',
            opts=['bold']
        )
        try:
            while True:
                _file = files.pop(0)
                print(self.format_diff(sep + _file))
                if files:
                    get_input('===')
        except KeyboardInterrupt:
            chalk.red('\nExit', opts=['bold'])
        except IndexError as err:
            chalk.magenta('\n\n######\n\nDiff Completed', opts=['bold'])
