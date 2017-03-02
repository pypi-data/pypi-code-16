import os
import unittest

from owbd_file_and_data_utilities import file_utils


class TestGetFiles(unittest.TestCase):

    def setUp(self):
        self.output = []
        self.file_dir = u'.{s}test_data{s}file_utils{s}get_files{s}'.format(s=os.sep)

    def tearDown(self):
        pass

    def test_default_file_type(self):

        self.output = file_utils.get_files(directory=self.file_dir)

        expected_output = [u'./test_data/file_utils/get_files/file1.json',
                           u'./test_data/file_utils/get_files/file1.txt',
                           u'./test_data/file_utils/get_files/file2.json',
                           u'./test_data/file_utils/get_files/file3.json',
                           u'./test_data/file_utils/get_files/file4.txt',
                           u'./test_data/file_utils/get_files/folder1']

        self.assertEqual(expected_output, self.output,
                         msg=u'Test get_files: Default extension: files do not match!')

    def test_default_file_type_recursive(self):
        self.output = file_utils.get_files(directory=self.file_dir,
                                           recursive=True)

        expected_output = [u'./test_data/file_utils/get_files/file1.json',
                           u'./test_data/file_utils/get_files/file1.txt',
                           u'./test_data/file_utils/get_files/file2.json',
                           u'./test_data/file_utils/get_files/file3.json',
                           u'./test_data/file_utils/get_files/file4.txt',
                           u'./test_data/file_utils/get_files/folder1/file5.txt',
                           u'./test_data/file_utils/get_files/folder1/file6.json',
                           u'./test_data/file_utils/get_files/folder1/folder2/file7.txt',
                           u'./test_data/file_utils/get_files/folder1/folder2/file8.json']

        self.assertEqual(expected_output, self.output,
                         msg=u'Test get_files: Default extension recursive: files do not match!')

    def test_non_default_file_type(self):

        self.output = file_utils.get_files(directory=self.file_dir,
                                           pattern=u'*.txt')

        expected_output = [u'./test_data/file_utils/get_files/file1.txt',
                           u'./test_data/file_utils/get_files/file4.txt']

        self.assertEqual(expected_output, self.output,
                         msg=u'Test get_files: Non default extension: files do not match!')

    def test_non_default_file_type_recursive(self):
        self.output = file_utils.get_files(directory=self.file_dir,
                                           pattern=u'*.txt',
                                           recursive=True)

        expected_output = [u'./test_data/file_utils/get_files/file1.txt',
                           u'./test_data/file_utils/get_files/file4.txt',
                           u'./test_data/file_utils/get_files/folder1/file5.txt',
                           u'./test_data/file_utils/get_files/folder1/folder2/file7.txt']

        self.assertEqual(expected_output, self.output,
                         msg=u'Test get_files: Non default extension recursive: files do not match!')

    def test_all_files(self):
        self.output = file_utils.get_files(directory=self.file_dir,
                                           pattern=u'*.*')

        expected_output = [u'./test_data/file_utils/get_files/file1.json',
                           u'./test_data/file_utils/get_files/file1.txt',
                           u'./test_data/file_utils/get_files/file2.json',
                           u'./test_data/file_utils/get_files/file3.json',
                           u'./test_data/file_utils/get_files/file4.txt']

        self.assertEqual(expected_output, self.output,
                         msg=u'Test get_files: All: files do not match!')

    def test_all_files_recursive(self):
        self.output = file_utils.get_files(directory=self.file_dir,
                                           pattern=u'*.*',
                                           recursive=True)

        expected_output = [u'./test_data/file_utils/get_files/file1.json',
                           u'./test_data/file_utils/get_files/file1.txt',
                           u'./test_data/file_utils/get_files/file2.json',
                           u'./test_data/file_utils/get_files/file3.json',
                           u'./test_data/file_utils/get_files/file4.txt',
                           u'./test_data/file_utils/get_files/folder1/file5.txt',
                           u'./test_data/file_utils/get_files/folder1/file6.json',
                           u'./test_data/file_utils/get_files/folder1/folder2/file7.txt',
                           u'./test_data/file_utils/get_files/folder1/folder2/file8.json']

        self.assertEqual(expected_output, self.output,
                         msg=u'Test get_files: All recursive: files do not match!')


class TestGetFilesDict(unittest.TestCase):

    def setUp(self):
        self.output = {}
        self.file_dir = u'.{s}test_data{s}file_utils{s}get_files{s}'.format(s=os.sep)

    def tearDown(self):
        pass

    def test_default_file_type(self):

        file_utils.get_files_dict(directory=self.file_dir,
                                  output_dict=self.output)

        expected_output = {u'file1': u'./test_data/file_utils/get_files/file1.json',
                           u'file2': u'./test_data/file_utils/get_files/file2.json',
                           u'file3': u'./test_data/file_utils/get_files/file3.json'}

        self.assertEqual(expected_output, self.output,
                         msg=u'Test get_files_dict: Default extension: files do not match!')

    def test_non_default_file_type(self):

        file_utils.get_files_dict(directory=self.file_dir,
                                  output_dict=self.output,
                                  file_type=u'.txt')

        expected_output = {u'file1': u'./test_data/file_utils/get_files/file1.txt',
                           u'file4': u'./test_data/file_utils/get_files/file4.txt'}

        self.assertEqual(expected_output, self.output,
                         msg=u'Test get_files_dict: Non default extension: files do not match!')


if __name__ == u'__main__':
    unittest.main()
