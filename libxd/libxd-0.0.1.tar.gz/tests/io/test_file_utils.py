# -*- coding: utf-8 -*-
#
# Created by libxd on 17-2-5.
#
from __future__ import absolute_import
import unittest
from libxd.io import FileUtils


class TestFileUtils(unittest.TestCase):
    def setUp(self):
        pass

    def test_file_name(self):
        path = '/path/to/index.html'
        self.assertEqual('index', FileUtils.file_name(path))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
