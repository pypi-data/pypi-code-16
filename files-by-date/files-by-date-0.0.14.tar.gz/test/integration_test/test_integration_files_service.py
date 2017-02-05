import datetime
import os
import shutil
from unittest import TestCase

from files_by_date.service.files_service import FilesService, Count
from test.integration_test import RESOURCES_INPUT_DIR


class TestIntegrationFilesService(TestCase):
    # TEST_DIR = f'.{os.sep}resources{os.sep}target_dir{os.sep}{datetime.datetime.now().microsecond}' # 3.6
    TEST_DIR = '.{os_sep}resources{os_sep}target_dir{os_sep}{time}'.format(os_sep=os.sep,
                                                                           time=datetime.datetime.now().microsecond)

    def setUp(self):
        os.makedirs(TestIntegrationFilesService.TEST_DIR)

    def tearDown(self):
        if os.path.exists(TestIntegrationFilesService.TEST_DIR):
            shutil.rmtree(TestIntegrationFilesService.TEST_DIR)

    def test_gather_files(self):
        files = FilesService.gather_files(RESOURCES_INPUT_DIR, list())
        assert len(files) == 4

    def test_group_files_by_modified_date(self):
        files = FilesService.gather_files(RESOURCES_INPUT_DIR, list())
        grouped_files = FilesService.group_files_by_modified_date(files)

        # NEED BETTER ASSERT
        assert grouped_files

    def test_copy_files(self):
        files = FilesService.gather_files(RESOURCES_INPUT_DIR, list())
        grouped_files = FilesService.group_files_by_modified_date(files)

        assert str(Count(copied=4, files=4)) == str(
            FilesService.copy_files(grouped_files, TestIntegrationFilesService.TEST_DIR, False))
        assert str(Count(copied=4, files=4)) == str(
            FilesService.copy_files(grouped_files, TestIntegrationFilesService.TEST_DIR, True))
        assert str(Count(skipped=4, files=4)) == str(
            FilesService.copy_files(grouped_files, TestIntegrationFilesService.TEST_DIR, False))

        shutil.rmtree(TestIntegrationFilesService.TEST_DIR)
        assert str(Count(copied=4, files=4)) == str(
            FilesService.copy_files(grouped_files, TestIntegrationFilesService.TEST_DIR, False))
