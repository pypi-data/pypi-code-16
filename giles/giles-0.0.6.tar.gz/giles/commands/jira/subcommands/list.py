from __future__ import unicode_literals, print_function, absolute_import
from .. import JiraCommand


class List(JiraCommand):

    def add_arguments(self):
        self.parser.add_argument(
            '--users',
            help='List all of the users',
            action='store_true'
        )

        self.parser.add_argument(
            '--comments',
            help=(
                'List all of the comments for the given issue key.'
                'Defaults to the current active branch name.'
            ),
            default='active_branch'
        )

        self.parser.add_argument(
            '--search',
            help='List issues using the provided JQL string'
        )

        self.parser.add_argument(
            '--filter',
            help='List issues using the provided filter id'
        )

        self.parser.add_argument(
            '--favorite-filters',
            help='List all of your favorite filters by id and name.',
            action='store_true'
        )

        self.parser.add_argument(
            '--page',
            help='',
            default=0,
            type=int
        )

        self.parser.add_argument(
            '--limit',
            help='',
            type=int
        )

    def run(self, args):
        opts = {'page': args.page}
        if args.limit:
            opts['limit'] = args.limit

        if args.users:
            table = {
                'heading': ['NAME', 'KEY', 'ACTIVE'],
                'data': [
                    (user.displayName, user.key, user.active)
                    for user in self.users(**opts)
                ],
                'width': 24
            }
        elif args.search:
            table = {
                'heading': ['KEY', 'SUMMARY'],
                'data': [
                    (issue.key, issue.fields.summary)
                    for issue in self.search(args.search, **opts)
                ]
            }
        elif args.favorite_filters:
            table = {
                'heading': ['ID', 'NAME'],
                'data': [
                    (_filter.id, _filter.name)
                    for _filter in self.favorite_filters()
                ],
                'width': 5
            }
        elif args.filter:
            _filter = self.giles.jira.filter(args.filter)
            table = {
                'heading': ['KEY', 'SUMMARY'],
                'data': [
                    (issue.key, issue.fields.summary)
                    for issue in self.search(_filter.jql, **opts)
                ]
            }
        elif args.comments:
            branch = self.giles.repo.active_branch.name
            key = args.comments if args.comments != 'active_branch' else branch
            issue = self.giles.jira.issue(key)
            comments = self.giles.jira.comments(issue)
            table = {
                'heading': ['ID', 'AUTHOR', 'BODY'],
                'data': [
                    (comment.id, comment.author.key, comment.body)
                    for comment in comments
                ]
            }

        else:
            raise RuntimeError('Not a doctor...')

        return {'table': table}

    def search(self, jql, page=0, limit=5):
        offset = page * limit
        return self.giles.jira.search_issues(
            jql,
            startAt=offset,
            maxResults=limit
        )

    def users(self, page=0, limit=50):
        offset = page * limit
        return self.giles.jira.search_users(
            '_',
            startAt=offset,
            maxResults=limit
        )

    def favorite_filters(self):
        return self.giles.jira.favourite_filters()
