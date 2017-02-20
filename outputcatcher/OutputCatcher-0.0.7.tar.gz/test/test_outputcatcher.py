#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_outputcatcher.py
    Unit tests for OutputCatcher

    -Christopher Welborn 12-06-2016
"""

import os
import sys
import unittest

from outputcatcher import (
    __version__,
    ProcessOutput,
    StdErrCatcher,
    StdOutCatcher
)
SCRIPTDIR = os.path.abspath(sys.path[0])
if not SCRIPTDIR.endswith('/test'):
    SCRIPTDIR = os.path.join(SCRIPTDIR, 'test')
PROCOUTHELPER = os.path.join(SCRIPTDIR, 'processoutput_test_helper.py')


class OutputCatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # A map of catcher classes and the file object they should catch.
        print('Testing outputcatcher v. {}\n'.format(__version__))

    @staticmethod
    def get_fileobj_name(f):
        """ Retrieve any usable name for a file object, even if it's a
            class name. This is due to unittest wrapping output with a
            green.output.GreenStream.
        """
        return getattr(
            f,
            'name',
            getattr(f, '__name__', type(f).__name__)
        )

    def test_both_catchers(self):
        """ Both catchers should run as a context manager at the same time.
        """
        teststr = 'This is a test for both catchers.'
        teststrerr = 'This is a stderr test for both cathers.'
        with StdOutCatcher() as out:
            with StdErrCatcher() as err:
                sys.stdout.write(teststr)
                sys.stderr.write(teststrerr)

        self.assertEqual(
            err.output,
            teststrerr,
            msg='Failed to catch output on {}!'.format(
                self.get_fileobj_name(sys.stderr),
            )
        )
        self.assertEqual(
            out.output,
            teststr,
            msg='Failed to catch output on {}!'.format(
                self.get_fileobj_name(sys.stdout),
            )
        )

    def test_StdErrCatcher(self):
        """ StdErrCatcher should run as a context manager. """
        teststr = 'This is a test for StdErrCatcher.'

        with StdErrCatcher() as out:
            sys.stderr.write(teststr)
        self.assertEqual(
            out.output,
            teststr,
            msg='Failed to catch output on {} with StdErrCatcher!'.format(
                self.get_fileobj_name(sys.stderr),
            )
        )

    def test_StdErrCatcher_escaped(self):
        """ StdErrCatcher should escape output. """
        teststr = '\tThis is a test for StdErrCatcher.\n'

        with StdErrCatcher(escaped=True) as out:
            sys.stderr.write(teststr)
        self.assertEqual(
            out.output,
            repr(teststr)[1:-1],
            msg='Failed to escape output on {} with StdErrCatcher!'.format(
                self.get_fileobj_name(sys.stderr),
            )
        )

    def test_StdErrCatcher_maxlength(self):
        """ StdErrCatcher should trim to max-length. """
        teststr = 'This is a test for StdErrCatcher.'

        maxlength = 10
        with StdErrCatcher(max_length=maxlength) as out:
            sys.stderr.write(teststr)
            # Further calls should not write, and return 0.
            self.assertEqual(
                sys.stderr.write('okay'),
                0,
                msg='Failed to block write() when max length was exceeded.'
            )

        self.assertLessEqual(
            len(out.output),
            maxlength,
            msg='Failed to trim output length for StdErrCatcher!'
        )

        self.assertEqual(
            out.output,
            teststr[:maxlength],
            msg='Failed to trim output on {} with StdErrCatcher!'.format(
                self.get_fileobj_name(sys.stderr),
            )
        )

    def test_StdOutCatcher(self):
        """ StdOutCatcher should run as a context manager. """
        teststr = 'This is a test for StdOutCatcher.'

        with StdOutCatcher() as out:
            sys.stdout.write(teststr)
        self.assertEqual(
            out.output,
            teststr,
            msg='Failed to catch output on {} with StdOutCatcher!'.format(
                self.get_fileobj_name(sys.stdout),
            )
        )

    def test_StdOutCatcher_escaped(self):
        """ StdOutCatcher should escape output. """
        teststr = '\tThis is a test for StdOutCatcher.\n'

        with StdOutCatcher(escaped=True) as out:
            sys.stdout.write(teststr)
        self.assertEqual(
            out.output,
            repr(teststr)[1:-1],
            msg='Failed to escape output on {} with StdOutCatcher!'.format(
                self.get_fileobj_name(sys.stdout),
            )
        )

    def test_StdOutCatcher_maxlength(self):
        """ StdOutCatcher should trim to max length. """
        teststr = 'This is a test for StdOutCatcher.'

        maxlength = 10
        with StdOutCatcher(max_length=maxlength) as out:
            sys.stdout.write(teststr)
            # Further calls should not write, and return 0.
            self.assertEqual(
                sys.stdout.write('okay'),
                0,
                msg='Failed to block write() when max length was exceeded.'
            )

        self.assertLessEqual(
            len(out.output),
            maxlength,
            msg='Failed to trim output length for StdOutCatcher!'
        )

        self.assertEqual(
            out.output,
            teststr[:maxlength],
            msg='Failed to trim output on {} with StdOutCatcher!'.format(
                self.get_fileobj_name(sys.stdout),
            )
        )


class ProcessOutputTests(unittest.TestCase):
    """ Tests for the ProcessOutput object. """

    def get_helper_args(self, **kwargs):
        """ Build a command to run the ProcessOutput test helper, with correct
            arguments for the helper script.
            The kwargs are flag names and values for the script.
        """
        cmdargs = set()
        for k in kwargs or {'stdout': True}:
            if kwargs[k]:
                cmdargs.add('--{}'.format(k.lower()))
        cmd = [sys.executable, PROCOUTHELPER]
        cmd.extend(cmdargs)
        return cmd

    @unittest.skipUnless(
        os.path.exists(PROCOUTHELPER),
        'Missing {}.'.format(PROCOUTHELPER)
    )
    def test_ProcessOutput_output(self):
        """ ProcessOutput.output should catch both stdout and stderr. """
        with ProcessOutput(self.get_helper_args(stdout=True)) as out:
            self.assertGreater(
                len(out.stdout),
                0,
                msg='Failed to get stdout output from ProcessOutput!'
            )
        with ProcessOutput(self.get_helper_args(stderr=True)) as out:
            self.assertGreater(
                len(out.stderr),
                0,
                msg='Failed to get stderr output from ProcessOutput!'
            )
        with ProcessOutput(
                self.get_helper_args(
                    stdout=True,
                    stderr=True,
                    name=True)) as out:
            self.assertGreater(
                len(out.stderr),
                0,
                msg=' '.join((
                    'Failed to get stderr output from ProcessOutput',
                    'when both stdout/stderr are available!',
                ))
            )
            self.assertGreater(
                len(out.stdout),
                0,
                msg=' '.join((
                    'Failed to get stdout output from ProcessOutput',
                    'when both stdout/stderr are available!',
                ))
            )
            self.assertIn(
                b'stdout',
                out.stdout,
                msg='Output did not match the expected format, no name.'
            )
            self.assertIn(
                b'stderr',
                out.stderr,
                msg='Output did not match the expected format, no name.'
            )

    @unittest.skipUnless(
        os.path.exists(PROCOUTHELPER),
        'Missing {}.'.format(PROCOUTHELPER)
    )
    def test_ProcessOutput_stdin(self):
        """ ProcessOutput should pipe stdin as a string to the process. """
        stdinstr = 'This is a test.'
        with ProcessOutput(
                self.get_helper_args(stdin=True), stdin_data=stdinstr) as out:
            self.assertGreater(
                len(out.stdout),
                0,
                msg='Failed to get output when piping stdin data!'
            )
            self.assertEqual(
                out.stdout.decode(),
                stdinstr,
                msg='Failed to pipe stdin data, and receive it from `cat`!'
            )

    @unittest.skipUnless(
        os.path.exists(PROCOUTHELPER),
        'Missing {}.'.format(PROCOUTHELPER)
    )
    def test_ProcessOutput_stdin_bytes(self):
        """ ProcessOutput should pipe stdin as bytes to the process. """
        stdinbytes = 'This is a test.'.encode()
        with ProcessOutput(
                self.get_helper_args(stdin=True),
                stdin_data=stdinbytes) as out:
            self.assertGreater(
                len(out.stdout),
                0,
                msg='Failed to get output when piping stdin data!'
            )
            self.assertEqual(
                out.stdout,
                stdinbytes,
                msg='Failed to pipe stdin data, and receive it from `cat`!'
            )

    @unittest.skipUnless(
        os.path.exists(PROCOUTHELPER),
        'Missing {}.'.format(PROCOUTHELPER)
    )
    def test_ProcessOutput_iter(self):
        """ ProcessOutput should iterate over stderr/stdout data. """
        stdinstr = 'this\nis\na\ntest'
        expected = [
            b'this',
            b'is',
            b'a',
            b'test',
        ]
        p = ProcessOutput(
            self.get_helper_args(stdin=True, stream=True),
            stdin_data=stdinstr
        )
        self.assertListEqual(
            list(p.iter_stdout()),
            expected,
            msg='Failed to accurately iterate over stdout output.'
        )
        # stderr should be the same.
        p = ProcessOutput(
            self.get_helper_args(stdin=True, stream=True, stderr=True),
            stdin_data=stdinstr
        )
        self.assertListEqual(
            list(p.iter_stderr()),
            expected,
            msg='Failed to accurately iterate over stderr output.'
        )


if __name__ == '__main__':
    sys.exit(unittest.main(argv=sys.argv))
