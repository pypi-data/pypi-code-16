# -*- coding: utf-8 -*-

from shire.pool import Pool
from shire.workhorse import Workhorse
from app.jobs import TestRestartJob
from utils import TestBase
from shire.models import JobEntry as JobModel


class TestJobRestart(TestBase):

    def setUp(self):
        self.job = TestRestartJob.delay(
            config=self.config,
            pool='test_pool',
            queue='abc',
            kwargs=dict(sleep=0.1),
        )
        self.redis.flushall()
        self.pool = Pool(config=self.config, name='test_pool')

    def test_run(self):
        workhorse = Workhorse(pool=self.pool, job_id=self.job.id)
        workhorse.run()
        job_desc = JobModel.get(JobModel.id == self.job.id)
        self.assertEquals(job_desc.status, JobModel.STATUS_RESTART)
