# maildrake/smtp/tests/test_service.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit tests for `service` module. """

import asyncore
import io
import os
import sys
import types
import unittest
import unittest.mock

import faker
import testscenarios

import maildrake
import maildrake.smtp
import maildrake.smtp.service


fake_factory = faker.Faker()


class ArgumentParser_TestCase(unittest.TestCase):
    """ Test cases for class `ArgumentParser`. """

    def setUp(self):
        """ Set up test fixtures. """
        self.instance = maildrake.smtp.service.ArgumentParser()
        super().setUp()

    def test_instantiate(self):
        """ New `ArgumentParser` instance should be created. """
        self.assertIsNotNone(self.instance)

    def test_has_default_description(self):
        """ Should have default descripion value. """
        expected_description = "Mail Drake SMTP server"
        self.assertEqual(self.instance.description, expected_description)

    def test_has_specified_description(self):
        """ Should have default descripion value. """
        test_description = fake_factory.paragraph()
        self.instance = maildrake.smtp.service.ArgumentParser(
                description=test_description)
        expected_description = test_description
        self.assertEqual(self.instance.description, expected_description)

    def test_has_expected_argument_definitions(self):
        """ Should have expected argument definitions. """
        expected_argument_dests = [
                'address',
                ]
        argument_dests = [
                arg.dest for arg in self.instance._actions]
        for dest in expected_argument_dests:
            with self.subTest(argument_dest=dest):
                self.assertIn(dest, argument_dests)


class ArgumentParser_parse_args_TestCase(unittest.TestCase):
    """ Test cases for method `ArgumentParser.parse_args`. """

    def setUp(self):
        """ Set up test fixtures. """
        super().setUp()
        self.patch_program_name()
        self.instance = maildrake.smtp.service.ArgumentParser(
            prog=self.test_program_name)

    def patch_program_name(self):
        """ Patch the program command name in the command-line arguments. """
        self.test_program_name = fake_factory.word()
        fake_argv = list(sys.argv)
        fake_argv[0] = self.test_program_name

        attribute_patcher = unittest.mock.patch.object(
            sys, 'argv', new=fake_argv)
        attribute_patcher.start()
        self.addCleanup(attribute_patcher.stop)

    @unittest.mock.patch.object(sys, 'stdout', new_callable=io.StringIO)
    def test_help_option_emits_help_text(
            self,
            fake_stdout,
            ):
        """ Should emit help text when ‘--help’ option. """
        expected_output = "usage: {program}".format(
                program=self.test_program_name)
        for option in ["-h", "--help"]:
            with self.subTest(option=option):
                test_command_args = [option]
                with self.assertRaises(SystemExit):
                    self.instance.parse_args(test_command_args)
                self.assertIn(expected_output, fake_stdout.getvalue())

    @unittest.mock.patch.object(sys, 'stdout', new_callable=io.StringIO)
    def test_help_option_raises_systemexit(
            self,
            fake_stdout,
            ):
        """ Should raise SystemExit when ‘--help’ option. """
        for option in ["-h", "--help"]:
            with self.subTest(option=option):
                test_command_args = [option]
                with self.assertRaises(SystemExit):
                    self.instance.parse_args(test_command_args)

    @unittest.mock.patch.object(sys, 'stdout', new_callable=io.StringIO)
    def test_version_option_emits_program_version(
            self,
            fake_stdout,
            ):
        """ Should emit help text when ‘--version’ option. """
        test_command_args = ["--version"]
        with self.assertRaises(SystemExit):
            self.instance.parse_args(test_command_args)
        expected_output = "{program} {version}\n".format(
                program=self.test_program_name,
                version=maildrake._metadata.version_text)
        self.assertEqual(expected_output, fake_stdout.getvalue())

    @unittest.mock.patch.object(sys, 'stdout', new_callable=io.StringIO)
    def test_version_option_raises_systemexit(
            self,
            fake_stdout,
            ):
        """ Should raise SystemExit when ‘--version’ option. """
        test_command_args = ["--version"]
        with self.assertRaises(SystemExit):
            self.instance.parse_args(test_command_args)


def setup_SMTPApplication_fixture(testcase):
    """ Set up a test fixture for `SMTPApplication`.

        :param testcase:
            Instance of `TestCase` to which the fixture should be
            added. Must have a `test_app_class` attribute which will
            be used to instantiate the test fixture.
        :return: ``None``.

        """
    testcase.test_app = testcase.test_app_class()


class SMTPApplication_TestCase(unittest.TestCase):
    """ Test cases for class `SMTPApplication`. """

    test_command_name = "progname"

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_app_class = maildrake.smtp.service.SMTPApplication
        setup_SMTPApplication_fixture(self)

    def test_instantiate(self):
        """ Should create a `SMTPApplication` instance. """
        self.assertIsNotNone(self.test_app)


class SMTPApplication_parse_commandline_TestCase(unittest.TestCase):
    """ Test cases for class `SMTPApplication.parse_commandline`. """

    test_command_name = "progname"

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_app_class = maildrake.smtp.service.SMTPApplication
        setup_SMTPApplication_fixture(self)

        self.test_args = {
                'argv': [self.test_command_name],
                }

    def test_requires_argv(self):
        """ Should require commandline args list. """
        self.test_args = dict()
        with self.assertRaises(TypeError):
            self.test_app.parse_commandline(**self.test_args)

    def test_init_parses_args(self):
        """ SMTPApplication should parse commandline args list. """
        argv = self.test_args['argv']
        args_return = argv[1:]

        mock_parser = unittest.mock.Mock(name='ArgumentParser')
        fake_args = types.SimpleNamespace(
                address=":".join(
                    [fake_factory.word(), str(fake_factory.pyint())]),
                )
        mock_parser.parse_args.return_value = fake_args

        with unittest.mock.patch.object(
                maildrake.smtp.service, 'ArgumentParser'
                ) as mock_ArgumentParser_class:
            mock_ArgumentParser_class.return_value = mock_parser
            self.test_app.parse_commandline(**self.test_args)
        mock_parser.parse_args.assert_called_once_with(args_return)

    def test_init_sets_specified_args(self):
        """ SMTPApplication should set the specified commandline arguments. """
        self.test_args.update(argv=["progname", "foo:17"])
        (progname, expected_address) = self.test_args['argv']
        self.test_app.parse_commandline(**self.test_args)
        args = self.test_app.args
        self.assertEqual(args.address, expected_address)


class SMTPApplication_parse_commandline_ErrorTestCase(
        testscenarios.WithScenarios,
        unittest.TestCase):
    """ Error test cases for class `SMTPApplication.parse_commandline`. """

    test_command_name = "progname"

    scenarios = [
            ('args-zero', {
                'test_argv': [],
                'expected_error': IndexError,
                }),
            ('args-three', {
                'test_argv': [test_command_name, "foo", "bar"],
                'expected_error': SystemExit,
                }),
            ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_app_class = maildrake.smtp.service.SMTPApplication
        setup_SMTPApplication_fixture(self)

        self.test_args = {
                'argv': self.test_argv,
                }

    def test_init_rejects_incorrect_commandline_args_count(self):
        """ Should reject incorrect count of commandline args. """
        with unittest.mock.patch.object(sys, 'stderr'):
            with self.assertRaises(self.expected_error):
                self.test_app.parse_commandline(**self.test_args)


@unittest.mock.patch.object(asyncore, 'loop')
@unittest.mock.patch.object(maildrake.smtp, 'SMTPServer')
class SMTPApplication_run_TestCase(unittest.TestCase):
    """ Test cases for method `SMTPApplication.run`. """

    test_command_name = "progname"

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.test_app_class = maildrake.smtp.service.SMTPApplication
        setup_SMTPApplication_fixture(self)

        self.fake_address = maildrake.config.ServerAddress(
                host=fake_factory.word(),
                port=fake_factory.pyint(),
                )
        self.test_app.address = self.fake_address

    def test_run_performs_required_steps(
            self,
            mock_smtpserver_class,
            mock_asyncore_loop,
            ):
        """ Should perform steps required for application. """
        mock_app = unittest.mock.MagicMock(
                maildrake.smtp.service.SMTPApplication,
                wraps=maildrake.smtp.service.SMTPApplication)

        self.test_app.run()
        mock_smtpserver_class.assert_called_once_with(
                localaddr=self.fake_address)
        mock_asyncore_loop.assert_called_once_with()


@unittest.mock.patch.object(maildrake.smtp.service, 'SMTPApplication')
class main_TestCase(unittest.TestCase):
    """ Test cases for function `main`. """

    test_command_name = "progname"

    def setUp(self):
        """ Set up fixtures for this test case. """
        self.test_args = {
                'argv': [self.test_command_name],
                }

    def test_calls_app_parse_commandline_with_specified_argv(
            self,
            mock_app_class,
    ):
        """ Should call app's `parse_commandline` method with `argv`. """
        maildrake.smtp.service.main(**self.test_args)
        expected_app = mock_app_class.return_value
        expected_argv = self.test_args['argv']
        expected_app.parse_commandline.assert_called_with(expected_argv)

    def test_calls_app_parse_commandline_with_commandline_argv(
            self,
            mock_app_class,
    ):
        """ Should call app's `parse_commandline` method with `sys.argv`. """
        del self.test_args['argv']
        with unittest.mock.patch.object(sys, 'argv') as mock_sys_argv:
            maildrake.smtp.service.main(**self.test_args)
            expected_argv = mock_sys_argv
        expected_app = mock_app_class.return_value
        expected_app.parse_commandline.assert_called_with(expected_argv)

    def test_calls_app_run(
            self,
            mock_app_class,
    ):
        """ Should call app's `run` method. """
        maildrake.smtp.service.main(**self.test_args)
        expected_app = mock_app_class.return_value
        expected_app.run.assert_called_with()

    def test_returns_status_okay_when_no_error(
            self,
            mock_app_class,
    ):
        """ Should return “okay” exit status when no error. """
        result = maildrake.smtp.service.main(**self.test_args)
        expected_result = os.EX_OK
        self.assertEqual(result, expected_result)

    def test_returns_exit_status_when_parse_commandline_systemexit(
            self,
            mock_app_class,
    ):
        """ Should return exit status from `parse_commandline` SystemExit. """
        expected_app = mock_app_class.return_value
        test_exit_status = fake_factory.pyint()
        test_exception = SystemExit(test_exit_status)
        with unittest.mock.patch.object(
                expected_app, 'parse_commandline',
                side_effect=test_exception):
            result = maildrake.smtp.service.main(**self.test_args)
        expected_result = test_exit_status
        self.assertEqual(result, expected_result)

    def test_returns_exit_status_when_run_systemexit(
            self,
            mock_app_class,
    ):
        """ Should return exit status from `run` SystemExit. """
        expected_app = mock_app_class.return_value
        test_exit_status = fake_factory.pyint()
        test_exception = SystemExit(test_exit_status)
        with unittest.mock.patch.object(
                expected_app, 'run',
                side_effect=test_exception):
            result = maildrake.smtp.service.main(**self.test_args)
        expected_result = test_exit_status
        self.assertEqual(result, expected_result)


# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.AGPL-3’ for details.


# Local variables:
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
