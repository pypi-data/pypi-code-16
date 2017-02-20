# -*- coding: utf-8 -*-
import io
import unittest

from pynlple.datasource.filesource import FilePathSource
from ..module import abs_path as path


class FileSourceTest(unittest.TestCase):

    def setUp(self):
        self.encoding = 'utf8'
        self.filepath1 = path(__file__, 'data/filesource/file1.txt')
        self.filepath2 = path(__file__, 'data/filesource/file2.txt')

    def test_should_two_readers_yield_lines_simultaneously(self):
        file1 = FilePathSource.open_file(self.filepath1)
        file2 = FilePathSource.open_file(self.filepath2)
        lines = [[next(file_) for file_ in [file1, file2]] for _ in range(4)]
        self.assertEqual(self.readlines(self.filepath1), [line[0] for line in lines])
        self.assertEqual(self.readlines(self.filepath2), [line[1] for line in lines])

    def readlines(self, filepath):
        return [line for line in io.open(filepath, 'rt', encoding=self.encoding)]
