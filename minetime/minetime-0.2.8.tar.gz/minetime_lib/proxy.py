# -*- coding: utf-8 -*-

from redmine import Redmine
from redmine.exceptions import ResourceNotFoundError, ValidationError


class RedmineProxy():

    def __init__(self, logger, uri, key):
        self.logger = logger
        self.redmine = Redmine(uri, key=key)
        self.logger.debug('redmine: %s', self.redmine)

    def _my_issues(self):
        return self.redmine.issue \
                           .filter(assigned_to_id='me', status_id='open') \
                           .values('id', 'subject')

    def get_issues(self, tracked_query_ids):
        return self._my_issues(), self._tracked_issues(tracked_query_ids)

    def _tracked_issues(self, tracked_query_ids):
        self.logger.debug('tracked_query_ids: %s', tracked_query_ids)
        tracked_issues_list = []
        if tracked_query_ids:
            for tracked_query_id in tracked_query_ids:
                tracked_issues = self.redmine.issue \
                    .filter(query_id=tracked_query_id) \
                    .values('id', 'subject')
                self.logger.debug('Nth tracked_issues length %s', len(tracked_issues))
                tracked_issues_list.append(tracked_issues)
        return tracked_issues_list

    def get_version_issues(self, vid):
        return self.redmine.issue.filter(fixed_version_id=vid)

    def get_project(self, project_id):
        try:
            return self.redmine.project.get(project_id)
        except ResourceNotFoundError:
            return False

    def post_timelog(self, t):
        '''
        No validation here.
        Input is sanitized upstream and redmine handles final validation.
        '''

        self.logger.debug('about to post timelog: %s', t)
        try:
            time_entry = self.redmine.time_entry.create(issue_id=t.issue_id,
                                                        hours=t.hours,
                                                        spent_on=t.spent_on,
                                                        activity_id=t.activity_id,
                                                        comments=t.comments)

            # Confirm/Feedback
            if time_entry:
                self.logger.debug('Added: issue_id %s, hours %s, activity_id %s, comments %s, spent_on %s',
                                t.issue_id, t.hours, t.activity_id, t.comments, t.spent_on)
            return True
        except ValidationError as e:
            return False

    def post_timelogs(self, timelogs):
        rejected_timelogs = []
        posted_timelogs = []
        for timelog in timelogs:
            if self.post_timelog(timelog):
                posted_timelogs.append(timelog)
            else:
                rejected_timelogs.append(timelog)
        return (posted_timelogs, rejected_timelogs)


def init_proxy(logger, config):
    uri = config['general']['uri']
    key = config['user']['api_key']
    proxy = RedmineProxy(logger, uri, key)
    return proxy
