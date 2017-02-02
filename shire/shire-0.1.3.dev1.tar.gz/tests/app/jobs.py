# -*- coding: utf-8 -*-
import time

from shire.job import Job


class TestSleepJob(Job):

    def __init__(self, workhorse):
        super(TestSleepJob, self).__init__(workhorse=workhorse)
        self.redis = self.workhorse.config.get_redis()

    def run(self, sleep=None):
        self.redis.set('test_job {}'.format(self.job_entry.id), 'STARTED')
        if sleep:
            time.sleep(sleep)
        self.redis.set('test_job {}'.format(self.job_entry.id), 'ENDED')


class TestRestartJob(Job):

    def __init__(self, workhorse):
        super(TestRestartJob, self).__init__(workhorse=workhorse)
        self.redis = self.workhorse.config.get_redis()

    def run(self, sleep=None):
        self.redis.set('restart_job {}'.format(self.job_entry.id), 'STARTED')
        if sleep:
            time.sleep(sleep)
        self.restart()
