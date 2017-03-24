# maildrake/tests/test_smtp.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit tests for `smtp` module. """

import asyncore
import email
import smtpd
import sqlite3
import unittest
import unittest.mock

import faker
import testscenarios

from .test_message import (
        WithMessageCompareTestCase,
        make_message_scenarios,
)
import maildrake.smtp
import maildrake.store.sqlite


fake_factory = faker.Faker()


def make_test_smtpserver(*args, **kwargs):
    """ Make an `SMTPServer` instance for test cases. """
    with unittest.mock.patch.object(asyncore.dispatcher, 'bind'):
        instance = maildrake.smtp.SMTPServer(*args, **kwargs)

    return instance


def setup_smtpserver_fixture(testcase):
    """ Set up an `SMTPServer` fixture for the `testcase`. """
    testcase.test_smtpserver_args = {
            'localaddr': ('localhost', 8025),
            'decode_data': True,
            }

    with unittest.mock.patch.object(asyncore.dispatcher, 'bind'):
        instance = make_test_smtpserver(**testcase.test_smtpserver_args)

    testcase.test_smtpserver = instance


class SMTPServer_TestCase(unittest.TestCase):
    """ Test cases for class `SMTPServer`. """

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        setup_smtpserver_fixture(self)

    def test_is_smtpd_smtpserver_instance(self):
        """ Should be instance of `smtpd.SMTPServer`. """
        self.assertIsInstance(self.test_smtpserver, smtpd.SMTPServer)

    def test_remoteaddr_is_none(self):
        """ Should have remote relay address of None. """
        self.assertIs(self.test_smtpserver._remoteaddr, None)

    def test_decode_data_default_is_true(self):
        """ Should default `decode_data` to True. """
        del self.test_smtpserver_args['decode_data']
        setup_smtpserver_fixture(self)
        self.assertTrue(self.test_smtpserver._decode_data)


@unittest.mock.patch.object(maildrake.store, 'sqlite')
class SMTPServer_process_message_TestCase(
        WithMessageCompareTestCase,
        testscenarios.WithScenarios,
        unittest.TestCase):
    """ Test cases for method `SMTPServer.process_message`. """

    scenarios = make_message_scenarios()

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()

        self.patch_get_database_file_path()

        setup_smtpserver_fixture(self)

        self.test_args = {
                'peer': object(),
                'mailfrom': object(),
                'rcpttos': object(),
                'data': self.raw_text,
                }

    def patch_get_database_file_path(self):
        """ Patch the `get_database_file_path` function for this test case. """
        func_patcher = unittest.mock.patch.object(
                maildrake.store.sqlite, 'get_database_file_path')
        mock_func = func_patcher.start()
        self.addCleanup(func_patcher.stop)

        self.fake_database_file_path = fake_factory.file_name()
        mock_func.return_value = self.fake_database_file_path

    def test_calls_connect_with_expected_database_path(
            self,
            mock_store_sqlite,
    ):
        """ Should call `connect` with expected path value. """
        self.test_smtpserver.process_message(**self.test_args)
        expected_path = self.fake_database_file_path
        mock_store_sqlite.connect.assert_called_with(expected_path)

    def test_calls_create_message_with_expected_connection(
            self,
            mock_store_sqlite,
    ):
        """ Should call `create_message` with expected `connection` value. """
        self.test_smtpserver.process_message(**self.test_args)
        expected_connection = mock_store_sqlite.connect.return_value
        mock_store_sqlite.create_message.assert_called_with(
                expected_connection, unittest.mock.ANY)

    def test_calls_create_message_with_expected_message(
            self,
            mock_store_sqlite,
    ):
        """ Should call `create_message` with expected `message` value. """
        self.test_smtpserver.process_message(**self.test_args)
        (args, kwargs) = mock_store_sqlite.create_message.call_args
        (__, message) = args
        self.assertEqual(message, self.test_message)

    def test_exits_connection_context_manager(
            self,
            mock_store_sqlite,
    ):
        """ Should exit the context manager of the database connection. """
        expected_connection = mock_store_sqlite.connect.return_value
        self.test_smtpserver.process_message(**self.test_args)
        expected_connection.__exit__.assert_called_with(
                unittest.mock.ANY, unittest.mock.ANY, unittest.mock.ANY)


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
