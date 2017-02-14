from unittest import TestCase
from unittest.mock import create_autospec

from nose.tools import istest, raises

from bigorna.commons.config import Config
from bigorna.tasks import TaskFactory, TaskDefinition


class TaskFactoryTest(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.out = "%s.out"
        self.config_mock = create_autospec(Config)
        self.config_mock.tasks = [{'name': 'ls', 'cmd': 'ls -la {dirname}'},
                                  {'name': 'cp', 'cmd': 'cp {orig} {dest}'}]
        self.factory = TaskFactory(self.config_mock)

    @istest
    def create_return_task_def(self):
        t_def = self.factory.create_task_definition('ls', {'dirname': '/home'}, self.out)

        self.assertEquals(t_def.cmd, 'ls -la /home')
        self.assertIsNotNone(t_def.output_file)

    @raises(KeyError)
    @istest
    def create_raise_error_if_not_enough_params(self):
        self.factory.create_task_definition('cp', {'orig': '/home'}, self.out)

    @raises(KeyError)
    @istest
    def create_raise_error_if_invalid_command(self):
        self.factory.create_task_definition('cd', {'dirname': '/home'}, self.out)


class TaskDefinitionTest(TestCase):
    @istest
    def create_task_def_generates_id(self):
        t_def = TaskDefinition("ls /", None)

        self.assertIsNotNone(t_def.id)
        self.assertIsInstance(t_def.id, str)

    @istest
    def create_task_def_sets_cwd(self):
        t_def = TaskDefinition("ls /", '/home', "%s.out")

        self.assertEquals(t_def.base_dir, '/home')

    @istest
    def create_task_output_from_id(self):
        t_def = TaskDefinition("ls /", None, "%s.out")

        self.assertEquals(t_def.output_file, "%s.out" % t_def.id)
