# maildrake/store/tests/test_sqlite.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Unit tests for `sqlite` module. """

import io
import os.path
import sqlite3
import textwrap
import types
import unittest
import unittest.mock

import faker
import testscenarios

from ... import config
from .. import sqlite


fake_factory = faker.Faker()


def patch_config_options(testcase):
    """ Patch `config.options` for the `testcase`.

        :param testcase: The `unittest.TestCase` instance for which to
            patch.
        :return: None.

        The `config.options` object is patched with the object
        `testcase.fake_config_options`.

        """
    patcher = unittest.mock.patch.object(
            config, 'options',
            new=testcase.fake_config_options)
    patcher.start()
    testcase.addCleanup(patcher.stop)


class get_database_file_path_TestCase(
        testscenarios.WithScenarios,
        unittest.TestCase):
    """ Test cases for function `get_database_file_path`. """

    fake_config_options = types.SimpleNamespace(
            DATABASE_DIR=fake_factory.file_name(),
            DATABASE_NAME=fake_factory.word(),
            )

    scenarios = [
            ('default', {
                'test_args': {},
                'expected_path': os.path.join(
                    fake_config_options.DATABASE_DIR,
                    fake_config_options.DATABASE_NAME + ".sqlite"),
                }),
            ('directory', {
                'test_args': {
                    'directory': "lorem",
                    },
                'expected_path': os.path.join(
                    "lorem",
                    fake_config_options.DATABASE_NAME + ".sqlite"),
                }),
            ('database-name', {
                'test_args': {
                    'name': "ipsum",
                    },
                'expected_path': os.path.join(
                    fake_config_options.DATABASE_DIR,
                    "ipsum.sqlite"),
                }),
            ('directory database-name', {
                'test_args': {
                    'directory': "lorem",
                    'name': "ipsum",
                    },
                'expected_path': os.path.join(
                    "lorem",
                    "ipsum.sqlite"),
                }),
            ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        patch_config_options(self)

    def test_returns_expected_path(self):
        """ Should return the expected path value. """
        result = sqlite.get_database_file_path(**self.test_args)
        self.assertEqual(result, self.expected_path)


def patch_sqlite3(testcase):
    """ Patch the `sqlite3` module for this test case.

        :param testcase: The `unittest.TestCase` instance for which to
            patch.
        :return: None.

        """
    module_patcher = unittest.mock.patch.object(sqlite, 'sqlite3')
    testcase.mock_sqlite3 = module_patcher.start()
    testcase.addCleanup(module_patcher.stop)


class connect_TestCase(unittest.TestCase):
    """ Test cases for function `connect`. """

    def setUp(self):
        """ Set up fixtures for this test case. """
        patch_sqlite3(self)

    def test_connects_to_specified_path(self):
        """ Should connect to the specified file path. """
        file_path = fake_factory.file_name(extension=".sqlite")
        sqlite.connect(file_path)
        self.mock_sqlite3.connect.assert_called_with(file_path)

    def test_returns_connection_object(self):
        """ Should return the connection object. """
        file_path = fake_factory.file_name(extension=".sqlite")
        result = sqlite.connect(file_path)
        expected_result = self.mock_sqlite3.connect.return_value
        self.assertIs(result, expected_result)


class get_schema_from_file_TestCase(
        testscenarios.WithScenarios,
        unittest.TestCase):
    """ Test cases for function `get_schema_from_file`. """

    scenarios = [
            ('3-statements', {
                'test_infile_content': textwrap.dedent("""\
                    CREATE TABLE lorem ();
                    DROP TABLE lorem;
                    SELECT NULL;
                    """),
                'expected_statements': [
                    "CREATE TABLE lorem ();",
                    "DROP TABLE lorem;",
                    "SELECT NULL;",
                    ],
                }),
            ('2-statements 1-blank', {
                'test_infile_content': textwrap.dedent("""
                    CREATE TABLE lorem ();

                    DROP TABLE lorem;
                    """),
                'expected_statements': [
                    "CREATE TABLE lorem ();",
                    "DROP TABLE lorem;",
                    ],
                }),
            ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        self.test_infile = io.StringIO(self.test_infile_content)

    def test_returns_expected_statements(self):
        """ Should return the expected statements. """
        result = sqlite.get_schema_from_file(self.test_infile)
        self.assertEqual(result, self.expected_statements)


class get_schema_TestCase(
        testscenarios.WithScenarios,
        unittest.TestCase):
    """ Test cases for function `get_schema`. """

    fake_config_options = types.SimpleNamespace(
            DATABASE_SCHEMA=fake_factory.file_name(),
            )

    def setUp(self):
        """ Set up fixtures for this test case. """
        patch_config_options(self)
        self.patch_open()
        self.patch_get_schema_from_file()

    def patch_open(self):
        """ Patch the `open` builtin for this test case. """
        self.mock_open = unittest.mock.mock_open()

    def patch_get_schema_from_file(self):
        """ Patch the `get_schema_from_file` function for this test case. """
        func_patcher = unittest.mock.patch.object(
                sqlite, 'get_schema_from_file')
        self.mock_get_schema_from_file = func_patcher.start()
        self.addCleanup(func_patcher.stop)

    def test_opens_specified_infile(self):
        """ Should open the specified input file. """
        test_infile_path = fake_factory.file_name()
        with unittest.mock.patch('builtins.open', self.mock_open):
            sqlite.get_schema(test_infile_path)
        self.mock_open.assert_called_with(test_infile_path)

    def test_opens_configured_infile_by_default(self):
        """ Should open the configure input file by default. """
        with unittest.mock.patch('builtins.open', self.mock_open):
            sqlite.get_schema()
        expected_path = self.fake_config_options.DATABASE_SCHEMA
        self.mock_open.assert_called_with(expected_path)

    def test_calls_get_schema_from_file(self):
        """ Should call `get_schema_from_file` with opened file. """
        with unittest.mock.patch('builtins.open', self.mock_open):
            sqlite.get_schema()
        expected_file = self.mock_open.return_value
        self.mock_get_schema_from_file.assert_called_with(expected_file)


class init_TestCase(
        testscenarios.WithScenarios,
        unittest.TestCase):
    """ Test cases for function `init`. """

    scenarios = [
            ('simple', {
                'schema': [
                    "DROP TABLE lorem;",
                    "CREATE TABLE lorem (dolor INTEGER);",
                    ],
                'expected_statements': [
                    "DROP TABLE lorem;",
                    "CREATE TABLE lorem (dolor INTEGER);",
                    ],
                }),
            ('long-statement', {
                'schema': [
                    "DROP TABLE lorem;",
                    textwrap.dedent("""\
                        CREATE TABLE lorem (
                            dolor INTEGER,
                            sit CHARACTER VARYING(20),
                            PRIMARY KEY (dolor)
                        );
                        """),
                    ],
                'expected_statements': [
                    "DROP TABLE lorem;",
                    textwrap.dedent("""\
                        CREATE TABLE lorem (
                            dolor INTEGER,
                            sit CHARACTER VARYING(20),
                            PRIMARY KEY (dolor)
                        );
                        """),
                    ],
                }),
            ('statement-with-comment', {
                'schema': [
                    "DROP TABLE lorem;",
                    textwrap.dedent("""\
                        CREATE TABLE lorem (
                            dolor INTEGER,
                            -- We don't actually need this.
                            sit CHARACTER VARYING(20),
                            PRIMARY KEY (dolor)
                        );
                        """),
                    ],
                'expected_statements': [
                    "DROP TABLE lorem;",
                    textwrap.dedent("""\
                        CREATE TABLE lorem (
                            dolor INTEGER,
                            sit CHARACTER VARYING(20),
                            PRIMARY KEY (dolor)
                        );
                        """),
                    ],
                }),
            ]

    def setUp(self):
        """ Set up fixtures for this test case. """
        patch_sqlite3(self)

        self.mock_connection = unittest.mock.MagicMock(sqlite3.Connection)
        self.mock_sqlite3.connect.return_value = self.mock_connection

    def test_executes_each_statement_on_cursor(self):
        """ Should execute each statement in `schema` on a cursor. """
        mock_cursor = self.mock_connection.cursor.return_value
        sqlite.init(self.mock_connection, self.schema)
        mock_cursor.execute.assert_has_calls([
                unittest.mock.call(statement)
                for statement in self.expected_statements])

    def test_commits_after_all_statements(self):
        """ Should commit the transaction after all statements. """
        sqlite.init(self.mock_connection, self.schema)
        self.assertEqual(
                self.mock_connection.mock_calls[-1],
                unittest.mock.call.commit())


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
