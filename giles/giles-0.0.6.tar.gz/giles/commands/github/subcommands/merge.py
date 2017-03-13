from __future__ import unicode_literals, print_function, absolute_import
from .pull_request import PullRequestBase


class Merge(PullRequestBase):
    """
    Pull request merge interface
        https://developer.github.com/v3/pulls/reviews/
    """

    def add_arguments(self):
        self.add_base_arguments()
        self.parser.add_argument(
            '--method',
            type=str,
            default='merge',
            help='merge method for the pull request (*merge, squash, rebase)'
        )
        self.parser.add_argument(
            '-t',
            '--title',
            help='title to use for the merge'
        )

    def run(self, args):
        output = self.base_run(args)
        if self._continue:
            title = args.title or self.pr.title
            message = args.comment or self.pr.body
            self.merge(args.method, title, message)
            if not args.quiet:
                return self.format_reviews()
        else:
            return output

    def merge(self, method, title, message):
        # https://developer.github.com/v3/pulls/#merge-a-pull-request-merge-button
        resp = self.client.put(
            self.pr.url + '/merge',
            json={
                'sha': self.pr.head.sha,
                'merge_method': method,
                'commit_title': title,
                'commit_message': message
            }
        )
        resp.raise_for_status()
        return resp.json()
