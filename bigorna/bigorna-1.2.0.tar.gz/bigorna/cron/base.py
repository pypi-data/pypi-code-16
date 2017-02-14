from copy import copy
import logging
from threading import Thread
from time import sleep

import schedule

from bigorna.commons import Config
from bigorna.cron.parser import ScheduleParser


log = logging.getLogger(__name__)


class CronJob:
    def __init__(self, name, task, params):
        self.name = name
        self.task = task
        self.params = copy(params)
        self.params['submitter'] = 'CronJob'

    def __call__(self, bigorna):
        bigorna.submit(self.task, self.params)

    def __repr__(self):
        return "%s: %s(%s)" % (self.name, self.task, self.params)


class CronTab(Thread):
    def __init__(self, cfg: Config):
        super(CronTab, self).__init__(name="TaskChecker", daemon=True)
        self.scheduler = schedule.Scheduler()
        parser = ScheduleParser(self.scheduler, cfg.schedule, self.run_job)
        self.jobs = parser.parse()
        self.bigorna = None

    def run(self):
        if not self.bigorna:
            raise Exception("cannot start cron without setting bigorna")
        elif not self.scheduler.jobs:
            log.info('No cron jobs configured, skipping cron runner')
            return

        log.info('Loaded cron jobs:')
        for j in self.jobs:
            log.info("[CronJob] %s", j)
        log.info('Starting cron runner')

        while True:
            self.scheduler.run_pending()
            sleep(self.scheduler.idle_seconds)

    def run_job(self, cronjob):
        log.info("Running cron job %s", cronjob)
        cronjob(self.bigorna)
