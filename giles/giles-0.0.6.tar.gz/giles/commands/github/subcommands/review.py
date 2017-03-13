from __future__ import unicode_literals, print_function, absolute_import
from .pull_request import PullRequestBase


class Review(PullRequestBase):
    """
    Pull request review interface
        https://developer.github.com/v3/pulls/reviews/
    """

    def add_arguments(self):
        self.add_base_arguments()
        self.parser.add_argument(
            '-a',
            '--approve',
            help='approve the pull request',
            action='store_true'
        )
        self.parser.add_argument(
            '-r',
            '--reject',
            help='request changes to the pull request',
            action='store_true'
        )
        self.parser.add_argument(
            '--delete',
            help='delete a review',
        )

    def run(self, args):
        output = self.base_run(args)

        if self._continue:
            if args.delete:
                self.delete(args.delete)
            elif args.approve:
                self.approve(args.comment)
            elif args.reject:
                self.reject(args.comment)
            elif args.comment:
                self.comment(args.comment)

            if not args.quiet:
                return self.format_reviews()
        else:
            return output

    def draft_review(self):
        resp = self.client.post(self.pr.url + '/reviews', json={'body': ''})
        resp.raise_for_status()
        return resp.json()

    def submit_review(self, event, comment=None):
        draft = self.draft_review()
        resp = self.client.post(
            self.pr.url + '/reviews/{}/events'.format(draft['id']),
            json={'body': comment or '', 'event': event}
        )
        resp.raise_for_status()
        return resp.json()

    def approve(self, comment=None):
        # example error
        # {"message":"Validation Failed","errors":["Could not approve for pull request review. Can not approve your own pull request"],"documentation_url":"https://developer.github.com/v3/pulls/reviews/#submit-a-pull-request-review"}
        return self.submit_review('APPROVE', comment=comment)

    def reject(self, comment=None):
        return self.submit_review('REQUEST_CHANGES', comment=comment)

    def comment(self, comment=None):
        return self.submit_review('COMMENT', comment=comment)

    def delete(self, _id):
        resp = self.client.delete(self.pr.url + '/reviews/{}'.format(_id))
        resp.raise_for_status()
        return resp.json()
