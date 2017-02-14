from unittest import TestCase
from unittest.mock import create_autospec

from nose.tools import istest

from bigorna.commons import Event
from bigorna.tasks import TaskScheduler, TaskDefinition, task_status_changed_evt
from bigorna.tasks.executor import Executor
from bigorna.commons import Config


class TaskSchedulerTest(TestCase):
    def setUp(self):
        self.config_mock = create_autospec(Config)
        self.config_mock.concurrent_tasks = 1
        self.executor_mock = create_autospec(Executor)
        self.task_def = TaskDefinition("ls -la", '.')
        self.scheduler = TaskScheduler(self.config_mock, self.executor_mock)

    @istest
    def submit_calls_executor_and_submit_if_no_tasks(self):
        self.executor_mock.running_tasks_counter = 0

        self.scheduler.submit(self.task_def)

        self.executor_mock.submit.assert_called_once_with(self.task_def)

    @istest
    def submit_dont_submit_to_executor_if_too_many_tasks(self):
        self.executor_mock.running_tasks_counter = 1

        self.scheduler.submit(self.task_def)

        self.executor_mock.submit.assert_not_called()

    @istest
    def handle_event_and_submit_to_executor(self):
        self.executor_mock.running_tasks_counter = 1
        self.scheduler.submit(self.task_def)

        other_task = TaskDefinition("ls -la", None)
        self.scheduler.submit(other_task)

        self.executor_mock.running_tasks_counter = 0

        self.scheduler._event_handler(Event(task_status_changed_evt, None))

        self.executor_mock.submit.assert_called_once_with(self.task_def)
        self.assertEqual(self.scheduler.pending_tasks_counter, 1)

    @istest
    def handle_event_and_not_pending_tasks(self):
        self.executor_mock.running_tasks_counter = 0

        self.scheduler._event_handler(Event(task_status_changed_evt, None))

        self.executor_mock.submit.assert_not_called()
