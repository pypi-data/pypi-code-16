from __future__ import unicode_literals, print_function, absolute_import
from .. import GitHubCommand


class List(GitHubCommand):
    """
    List elements of the github project
    """

    def add_arguments(self):
        self.parser.add_argument(
            '-u',
            '--users',
            help='list users by id and name',
            action='store_true'
        )
        self.parser.add_argument(
            '-p',
            '--pull-requests',
            help='list pull request details - #, head, base, user and title',
            action='store_true'
        )

        self.parser.add_argument(
            '-b',
            '--branches',
            help='list branches by name and HEAD sha',
            action='store_true'
        )

    def run(self, args):

        if args.users:
            table = self.render_users()
        elif args.branches:
            table = self.render_branches()
        elif args.pull_requests:
            table = self.render_pull_requests()

        return {'table': table}


    def users(self):
        return self.repo.get_collaborators()

    def branches(self):
        return self.repo.get_branches()

    def pull_requests(self):
        return self.repo.get_pulls()

    def render_pull_requests(self):
        return {
            'heading': ['#', 'HEAD', 'BASE', 'USER', 'TITLE'],
            'data': [
                (
                    pr.number,
                    pr.head.ref,
                    pr.base.ref,
                    pr.user.login,
                    pr.title
                )
                for pr in self.pull_requests()
            ]
        }

    def render_branches(self):
        return {
            'heading': ['NAME', 'SHA'],
            'data': [
                (branch.name, branch.commit.sha)
                for branch in self.branches()
            ]
        }

    def render_users(self):
        return {
            'heading': ['ID', 'LOGIN'],
            'data': [(col.id, col.login,) for col in self.users()]
        }