from __future__ import absolute_import, unicode_literals

import os
import unittest
import subprocess


class TestV013Api(unittest.TestCase):
    @staticmethod
    def run_task(*args):
        process = subprocess.Popen(["bash", "-c",
                                    "cd {folder}; invoke {args}"
                                   .format(folder=os.path.join('fixtures', 'v0.13'),
                                           args=' '.join(args))],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr

    def test_task_without_args(self):
        rc, stdout, stderr = self.run_task('say_hello')
        self.assertEqual(rc, 0, msg=stderr)
        self.assertIn(b'Hello world', stdout)

    def test_task_with_dependencies(self):
        rc, stdout, stderr = self.run_task('greeting')
        self.assertEqual(rc, 0, msg=stderr)
        self.assertIn(b'Hello world', stdout)
        self.assertIn(b'Greeting!', stdout)

    def test_run_all(self):
        rc, stdout, stderr = self.run_task('say_hello_and_say_goodbye')
        self.assertEqual(rc, 0, msg=stderr)
        self.assertIn(b'Hello world', stdout)
        self.assertIn(b'Goodbye', stdout)
