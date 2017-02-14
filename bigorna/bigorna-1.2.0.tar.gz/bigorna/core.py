from threading import Barrier

from bigorna.commons import Config
from bigorna.commons.event_bus import bus, Event
from bigorna.cron import CronTab
from bigorna.tasks import TaskScheduler, TaskFactory, task_status_changed_evt
from bigorna.tasks.executor import Executor
from bigorna.tracker import JobTracker, Job


class NotInitializedError(Exception):
    pass


class Bigorna:
    def __init__(self, output_tpl, tracker: JobTracker, sched: TaskScheduler,
                 factory: TaskFactory, crontab: CronTab):
        self.output = output_tpl
        self._tracker = tracker
        self._sched = sched
        self._task_factory = factory
        self.crontab = crontab
        self.crontab.bigorna = self
        self.crontab.start()

    def submit(self, task_type, params) -> Job:
        task_def = self._task_factory.create_task_definition(task_type, params, self.output)
        job = self._tracker.create_job(task_def, params.get('submitter', 'anonymous'))
        self._sched.submit(task_def)
        return job

    def list_jobs(self):
        return self._tracker.list_jobs()

    def get_job(self, job_id) -> Job:
        return self._tracker.get_job(job_id)

    @staticmethod
    def new(cfg: Config):
        tracker = JobTracker(cfg)
        sched = TaskScheduler(cfg)
        factory = TaskFactory(cfg)
        crontab = CronTab(cfg)
        return Bigorna(cfg.output_pattern, tracker, sched, factory, crontab)


class Standalone:
    def __init__(self, executor: Executor, factory: TaskFactory):
        self._task_factory = factory
        self._executor = executor
        self._barrier = Barrier(2)
        self._success = False
        bus.register(self.__class__.__name__, self.task_changed)

    def submit(self, task_type, params):
        task_def = self._task_factory.create_task_definition(task_type, params)
        self._executor.submit(task_def)

    def join(self):
        self._barrier.wait()
        return self._success

    def task_changed(self, evt: Event):
        if (evt.evt_type == task_status_changed_evt and
                evt.content.has_finished):
            self._success = evt.content.is_success
            self._barrier.wait()

    @staticmethod
    def new(cfg: Config):
        executor = Executor(2)
        factory = TaskFactory(cfg)
        return Standalone(executor, factory)
