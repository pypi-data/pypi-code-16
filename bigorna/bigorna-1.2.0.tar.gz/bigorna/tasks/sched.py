from collections import deque
from threading import RLock

from bigorna.commons import bus, Event

from . import TaskDefinition, task_status_changed_evt
from .executor import Executor
from bigorna.commons import Config


class TaskScheduler:
    def __init__(self, cfg: Config, executor: Executor = None):
        self._max_tasks = cfg.concurrent_tasks
        self._executor = executor if executor else Executor(cfg.task_check_delay)
        self._pending_tasks = deque()
        self._monitor = RLock()
        bus.register(TaskScheduler.__class__.__name__, self._event_handler)

    @property
    def pending_tasks_counter(self):
        return len(self._pending_tasks)

    def submit(self, task_def: TaskDefinition):
        with self._monitor:
            self._pending_tasks.appendleft(task_def)
            self._try_execute()

    def _try_execute(self):
        with self._monitor:
            if (self._executor.running_tasks_counter < self._max_tasks and
                    self.pending_tasks_counter > 0):
                self._executor.submit(self._pending_tasks.pop())

    def _event_handler(self, evt: Event):
        if evt.evt_type == task_status_changed_evt:
            self._try_execute()
