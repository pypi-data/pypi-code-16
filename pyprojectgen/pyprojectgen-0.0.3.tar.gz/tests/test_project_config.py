from unittest import TestCase
from src.project_config import ProjectConfiguration
from tests.test_helpers import test_configuration, create_project_conf_file, remove_project_conf_file
import os


class TestProjectConfiguration(TestCase):

    def setUp(self):
        self.conf_path = os.getcwd() + "/tmp/"
        self.conf_file = "project.yml"
        self.file_path = self.conf_path + "/" + self.conf_file
        create_project_conf_file(self.conf_path, self.file_path, test_configuration)

    def __remove_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

    def __remove_dir(self, dir_path):
        if os.path.exists(dir_path):
            os.rmdir(dir_path)

    def tearDown(self):
        self.__remove_file(self.file_path)

    def test_parse_config(self):
        conf = ProjectConfiguration(self.file_path)
        self.assertTrue(conf.metadata)
        self.assertEqual("pyprojectgen", conf.metadata['NAME'])
        self.assertTrue(conf.readme)
        self.assertTrue(conf.license)

