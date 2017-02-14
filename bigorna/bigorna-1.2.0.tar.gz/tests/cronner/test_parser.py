from unittest import TestCase
from unittest.mock import Mock

from nose.tools import istest
import schedule
from bigorna.cron.base import ScheduleParser, CronJob
from datetime import time


class CronParserTest(TestCase):
    def setUp(self):
        self.scheduler = schedule.Scheduler()
        self.func_mock = Mock()
        data = [{'name': '1',
                 'when': [
                     'every 5 minutes'],
                 'task': 'a',
                 'params': {'a': 1, 'b': 2}},
                {'name': '2',
                 'when': [
                     'every monday at 10:00',
                     'every friday at 10:00'],
                 'task': 'a'
                 }]
        self.parser = ScheduleParser(self.scheduler, data, self.func_mock)

    @istest
    def parse_return_CronJob(self):
        jobs = self.parser.parse()

        self.assertEqual(len(jobs), 2)
        job_1 = jobs[0]
        self.assertEquals(job_1.name, '1')
        self.assertEquals(job_1.task, 'a')
        self.assertEquals(job_1.params, {'a': 1, 'b': 2, 'submitter': 'CronJob'})
        job_2 = jobs[1]
        self.assertEquals(job_2.name, '2')
        self.assertEquals(job_2.task, 'a')
        self.assertEquals(job_2.params, {'submitter': 'CronJob'})

    @istest
    def schedule_task_every_5_minutes(self):
        job = CronJob('1', 'a', {'a': 1, 'b': 2})
        self.parser.parse_when(['every 5 minutes'], job)

        sched_job = self.scheduler.jobs[0]
        self.assertEquals(sched_job.interval, 5)
        self.assertEquals(sched_job.unit, 'minutes')
        self.assertEquals(sched_job.job_func.func, self.func_mock)
        self.assertEquals(sched_job.job_func.args, (job,))

    @istest
    def schedule_task_at(self):
        job = CronJob('1', 'a', {'a': 1, 'b': 2})
        self.parser.parse_when(['every monday at 10:00'], job)

        sched_job = self.scheduler.jobs[0]
        self.assertEquals(sched_job.interval, 1)
        self.assertEquals(sched_job.unit, 'weeks')
        self.assertEquals(sched_job.at_time, time(10, 0))
        self.assertEquals(sched_job.job_func.func, self.func_mock)
        self.assertEquals(sched_job.job_func.args, (job,))
