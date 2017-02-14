import logging
import subprocess
from threading import RLock, Thread
import time

from bigorna.commons import bus, Event

from . import TaskDefinition, Status, task_status_changed_evt


log = logging.getLogger(__name__)


class Task:
    def __init__(self, definition: TaskDefinition):
        self.definition = definition
        self.__status = Status.PENDING
        self.__process = None

    @property
    def id(self):
        return self.definition.id

    @property
    def command(self):
        return self.definition.cmd

    @property
    def output_file(self):
        return self.definition.output_file

    @property
    def cwd(self):
        return self.definition.base_dir

    @property
    def has_finished(self):
        return self.status in (Status.SUCCESS, Status.FAILED)

    @property
    def is_success(self):
        return self.status is Status.SUCCESS

    @property
    def status(self):
        return self.__status

    def _set_status(self, value):
        log.info("[%s] Status changing from %s to %s", self.id, self.__status,
                 value)
        self.__status = value

    def _check_status(self) -> Status:
        if not self.has_finished:
            self.process.poll()
            result_code = self.process.returncode
            if result_code is not None:
                if self.process.returncode == 0:
                    self._set_status(Status.SUCCESS)
                else:
                    self._set_status(Status.FAILED)

                return self.status

    def __call__(self):
        self._set_status(Status.RUNNING)
        out = open(self.output_file, 'w+') if self.output_file else None
        self._launch(self.command.split(), self.cwd, out)

        log.info('[%s] Command "%s" launched with pid %s', self.id,
                 self.command, self.process.pid)

    def _launch(self, cmd, cwd, out):
        log.info("[%s] Launching command %s with cwd=%s and output=%s",
                 self.id, cmd, cwd, out)
        if out:
            self.process = subprocess.Popen(cmd,
                                            cwd=self.cwd,
                                            stdout=out, stderr=out)
        else:
            self.process = subprocess.Popen(cmd,
                                            cwd=self.cwd)

    def __str__(self):
        return "%s | %s | %s" % (self.id, self.status, self.command)


class _TaskChecker(Thread):
    def __init__(self, executor, delay):
        super(_TaskChecker, self).__init__(name="TaskChecker", daemon=True)
        self._executor = executor
        self._delay = delay

    def run(self):
        while True:
            time.sleep(self._delay)
            self._executor._check_tasks()


class Executor:
    def __init__(self, task_check_delay):
        self.running_tasks = []
        self._monitor = RLock()
        self._checker = _TaskChecker(self, task_check_delay)
        self._checker.start()

    @property
    def running_tasks_counter(self):
        return len(self.running_tasks)

    def submit(self, definition: TaskDefinition) -> Task:
        with self._monitor:
            t = Task(definition)
            log.info("Task %s submitted to executor", t.id)
            self.running_tasks.append(t)
            t()
            self._notify_change(t)
        return t

    def _check_tasks(self):
        with self._monitor:
            tasks, self.running_tasks = self.running_tasks, []

            for task in tasks:
                status = task._check_status()
                if status:
                    log.info("Task %s has finished", task)
                    self._notify_change(task)
                else:
                    self.running_tasks.append(task)

    def _notify_change(self, task: Task):
        bus.publish(Event(task_status_changed_evt, task))
