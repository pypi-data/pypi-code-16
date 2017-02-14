import time
from unittest import TestCase
from unittest.mock import patch

from nose.tools import istest

from bigorna.commons import bus
from bigorna.tasks import TaskDefinition, Status, task_status_changed_evt
from bigorna.tasks.executor import Executor


class ExecutorTest(TestCase):
    def setUp(self):
        self.executor = Executor(0.1)
        self.task_def = TaskDefinition("ls -la", None)

    @istest
    @patch("bigorna.tasks.executor.Task")
    def submit_creates_and_calls_task(self, task_class_mock):
        task_mock = task_class_mock.return_value

        result = self.executor.submit(self.task_def)

        self.assertIs(result, task_mock)
        task_class_mock.assert_called_once_with(self.task_def)
        task_mock.assert_called_once_with()

    @istest
    @patch("bigorna.tasks.executor.Task")
    def submit_add_task_to_running_tasks(self, task_class_mock):
        self.executor.submit(self.task_def)
        self.assertEqual(len(self.executor.running_tasks), 1)

    @istest
    @patch("bigorna.tasks.executor.Task")
    def checker_calls_task_remove_finished_task(self, task_class_mock):
        task_mock = task_class_mock.return_value

        task_mock._check_status.return_value = Status.SUCCESS
        self.executor.submit(self.task_def)
        self.executor._check_tasks()  # force checker to run

        task_mock._check_status.assert_called_once_with()
        self.assertEqual(len(self.executor.running_tasks), 0)

    @istest
    @patch("bigorna.tasks.executor.Task")
    def checker_calls_task_keep_running_task(self, task_class_mock):
        task_mock = task_class_mock.return_value
        task_mock._check_status.return_value = None

        self.executor.submit(self.task_def)
        self.executor._check_tasks()  # force checker to run

        task_mock._check_status.assert_called_once_with()
        self.assertEqual(len(self.executor.running_tasks), 1)

    @istest
    @patch("bigorna.tasks.executor.Task")
    def checker_keep_running_if_running_tasks(self, task_class_mock):
        task_mock = task_class_mock.return_value
        task_mock._check_status.return_value = None

        self.executor.submit(self.task_def)
        time.sleep(0.3)

        self.assertGreaterEqual(task_mock._check_status.call_count, 2)

    @istest
    @patch("bigorna.tasks.executor.Task")
    def executor_notifies_tasks_changes(self, task_class_mock):
        task_mock = task_class_mock.return_value
        task_mock._check_status.return_value = Status.FAILED

        def handler(evt):
            global evt_type
            global task
            evt_type = evt.evt_type
            task = evt.content

        bus.register("testing", handler)

        self.executor.submit(self.task_def)
        self.executor._check_tasks()  # force checker to run

        self.assertEqual(evt_type, task_status_changed_evt)
        self.assertEqual(task, task_mock)
