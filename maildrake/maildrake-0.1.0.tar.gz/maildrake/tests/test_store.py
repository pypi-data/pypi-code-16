# maildrake/tests/test_store.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit tests for database storage. """

import datetime
import os
import sqlite3
import tempfile
import unittest

import faker
import testscenarios

import maildrake
import maildrake.store

from .test_message import make_message_scenarios


fake_factory = faker.Faker()


class FakeDatetime(datetime.datetime):
    """ Fake datetime for patching. """

    _superclass = datetime.datetime

    def __new__(cls, *args, **kwargs):
        return cls._superclass.__new__(cls._superclass, *args, **kwargs)


def setup_database(testcase):
    """ Set up the application database fixture for the `testcase`. """
    (testcase.db_fd, testcase.db_filename) = tempfile.mkstemp()
    connection = maildrake.store.sqlite.connect(testcase.db_filename)
    schema = maildrake.store.sqlite.get_schema()
    maildrake.store.sqlite.init(connection, schema)


def teardown_database(testcase):
    """ Tear down the application database fixture for the `testcase`. """
    if testcase.db_fd is not None:
        os.close(testcase.db_fd)
        os.unlink(testcase.db_filename)


@unittest.mock.patch.object(sqlite3, 'connect')
class connect_TestCase(unittest.TestCase):
    """ Test cases for function `connect`. """

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()
        setup_database(self)

    def tearDown(self):
        """ Tear down fixtures for this test case. """
        teardown_database(self)
        super().tearDown()

    def test_connects_to_file(
            self,
            mock_sqlite3_connect,
    ):
        """ Should connect to the specified file. """
        maildrake.store.sqlite.connect(self.db_filename)
        mock_sqlite3_connect.assert_called_with(self.db_filename)

    def test_returns_sqlite_connection(
            self,
            mock_sqlite3_connect,
    ):
        """ Should return an SQLite3 connection. """
        connection = maildrake.store.sqlite.connect(self.db_filename)
        expected_type = type(mock_sqlite3_connect.return_value)
        self.assertIs(type(connection), expected_type)


class MailDrakeDatabaseTestCaseBase(unittest.TestCase):
    """ Base for test cases of Mail Drake database operations. """

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()
        setup_database(self)

        self.connection = maildrake.store.sqlite.connect(self.db_filename)

    def tearDown(self):
        """ Tear down fixtures for this test case. """
        self.connection.close()
        teardown_database(self)
        super().tearDown()


class create_message_TestCase(
        testscenarios.WithScenarios,
        MailDrakeDatabaseTestCaseBase):
    """ Test cases for function `create_message`. """

    scenarios = make_message_scenarios()

    def get_message_from_database(self, message):
        """ Get the corresponding record for `message` from the database. """
        cursor = self.connection.cursor()
        cursor.execute("""\
                SELECT
                    created_at,
                    message_id,
                    "date",
                    sender,
                    recipients,
                    subject,
                    "body",
                    mime_type,
                    "raw"
                FROM
                    message
                WHERE
                    message_id = :message_id
                """, {
                    'message_id': message.message_id,
                })
        row = cursor.fetchone()

        return row

    def test_created_at_current_timestamp(self):
        """ Should have `created_at` value of current timestamp. """
        test_timestamp = datetime.datetime(
                2017, 2, 19, 22, 8,
                tzinfo=datetime.timezone.utc)

        with unittest.mock.patch.object(
                datetime, 'datetime', new=FakeDatetime):
            with unittest.mock.patch.object(
                    FakeDatetime, 'utcnow', return_value=test_timestamp):
                maildrake.store.sqlite.create_message(
                        self.connection, self.test_message)
        row = self.get_message_from_database(self.test_message)
        expected_timestamp = test_timestamp
        expected_timestamp_text = expected_timestamp.isoformat(sep=" ")
        self.assertEqual(row['created_at'], expected_timestamp_text)

    def test_message_id_matches_message(self):
        """ Should have `message_id` value of specified message. """
        maildrake.store.sqlite.create_message(
                self.connection, self.test_message)
        row = self.get_message_from_database(self.test_message)
        expected_message_id = self.message_id
        self.assertEqual(row['message_id'], expected_message_id)

    def test_date_matches_message(self):
        """ Should have `date` value of specified message. """
        maildrake.store.sqlite.create_message(
                self.connection, self.test_message)
        row = self.get_message_from_database(self.test_message)
        expected_timestamp_text = self.message_date_timestamp.isoformat(sep=" ")
        self.assertEqual(row['date'], expected_timestamp_text)

    def test_sender_matches_message(self):
        """ Should have `sender` value of specified message. """
        maildrake.store.sqlite.create_message(
                self.connection, self.test_message)
        row = self.get_message_from_database(self.test_message)
        expected_sender = self.test_message['from']
        self.assertEqual(row['sender'], expected_sender)

    def test_recipients_matches_message(self):
        """ Should have `recipients` value of specified message. """
        maildrake.store.sqlite.create_message(
                self.connection, self.test_message)
        row = self.get_message_from_database(self.test_message)
        expected_recipients = self.test_message['to']
        self.assertEqual(row['recipients'], expected_recipients)

    def test_subject_matches_message(self):
        """ Should have `subject` value of specified message. """
        maildrake.store.sqlite.create_message(
                self.connection, self.test_message)
        row = self.get_message_from_database(self.test_message)
        expected_subject = self.test_message['subject']
        self.assertEqual(row['subject'], expected_subject)

    def test_body_matches_message(self):
        """ Should have `body` value of specified message. """
        maildrake.store.sqlite.create_message(
                self.connection, self.test_message)
        row = self.get_message_from_database(self.test_message)
        expected_body = self.test_message.get_payload()
        self.assertEqual(row['body'], expected_body)

    def test_mime_type_matches_message(self):
        """ Should have `mime_type` value matching message. """
        maildrake.store.sqlite.create_message(
                self.connection, self.test_message)
        row = self.get_message_from_database(self.test_message)
        expected_mime_type = self.test_message.get_content_type()
        self.assertEqual(row['mime_type'], expected_mime_type)

    def test_raw_matches_message(self):
        """ Should have `raw` value of raw message content. """
        maildrake.store.sqlite.create_message(
                self.connection, self.test_message)
        row = self.get_message_from_database(self.test_message)
        expected_raw_text = self.test_message.as_string()
        self.assertEqual(row['raw'], expected_raw_text)


class retrieve_message_TestCase(
        testscenarios.WithScenarios,
        MailDrakeDatabaseTestCaseBase):
    """ Test cases for function `retrieve_message`. """

    scenarios = make_message_scenarios()

    def setUp(self):
        """ Set up fixtures for this test case. """
        super().setUp()
        maildrake.store.sqlite.create_message(
                self.connection, self.test_message)

    def test_message_has_specified_message_id(self):
        """ Should return a message with the specified “Message-Id” value. """
        message = maildrake.store.sqlite.retrieve_message(
                self.connection, self.message_id)
        expected_field_value = "<{}>".format(self.message_id)
        self.assertEqual(message['message-id'], expected_field_value)


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
