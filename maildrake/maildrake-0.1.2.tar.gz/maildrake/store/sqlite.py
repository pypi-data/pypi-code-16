# maildrake/store/sqlite.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" SQLite storage back end. """

import datetime
import email
import logging
import os.path
import sqlite3
import textwrap

import sqlparse

from .. import config


logger = logging.getLogger(__package__)


def get_database_file_path(
        directory=None, name=None, suffix=".sqlite"):
    """ Get the filesystem path to the SQLite database file.

        :param directory: Filesystem path to the directory where the
            database file is located.
        :param name: The name of the database.
        :param suffix: The filename suffix for the database file.
        :return: The filesystem path to the database file.

        """
    if directory is None:
        directory = config.options.DATABASE_DIR
    if name is None:
        name = config.options.DATABASE_NAME
    logger.debug(
            "Database file path components:"
            " directory: {directory!r}"
            " name: {name!r}"
            " suffix: {suffix!r}"
            .format(
                directory=directory, name=name, suffix=suffix)
            )
    path = os.path.join(directory, "".join([name, suffix]))
    logger.debug(
            "Database file path: {!r}".format(path))
    return path


def connect(database_file_path):
    """ Get a connection to the database.

        :param database_file_path: The filesystem path to the SQLite
            database file.
        :return: The database connection.

        """
    logger.info(
            "Making connection to SQLite database {!r}".format(
                database_file_path))
    connection = sqlite3.connect(database_file_path)
    connection.row_factory = sqlite3.Row
    return connection


def get_schema_from_file(infile):
    """ Get the database schema definition from `infile`.

        :param infile: An open file object containing the schema
            statements.
        :return: The database schema, as a sequence of SQL statements.

        """
    with infile:
        statements = [
            statement for statement in sqlparse.split(infile.read())
            if statement.strip()]
    logger.info(
            "Found {:d} SQL statements".format(len(statements)))

    return statements


def get_schema(infile_path=None):
    """ Get the database schema definition.

        :param infile_path: The filesystem path from which to read the
            schema.
            Default: The configured `DATABASE_SCHEMA` option.
        :return: The database schema, as a sequence of SQL statements.

        """
    if infile_path is None:
        infile_path = config.options.DATABASE_SCHEMA

    logger.info(
            "Reading database schema from {!r}".format(infile_path))
    with open(infile_path) as infile:
        statements = get_schema_from_file(infile)

    return statements


def init(connection, schema):
    """ Initialise the database from the specified `schema`.

        :param connection: The SQLite database connection to use.
        :param schema: The database schema, as a sequence of SQL
            statements.
        :return: None.

        """
    cursor = connection.cursor()
    logger.info(
            "Initialising database from {:d} SQL statements".format(
                len(schema)))
    for statement_raw in schema:
        statement = sqlparse.format(
                statement_raw,
                reindent=False,
                strip_comments=True,
                keyword_case='upper')
        logger.debug(
                "Executing schema statement {!r}".format(statement))
        cursor.execute(statement)

    logger.info(
            "Database initialisation complete,"
            " executed {:d} statements"
            .format(len(schema)))
    connection.commit()


datetime_format_rfc5322 = "%a, %d %b %Y %H:%M:%S %z"


def create_message(connection, message):
    """ Create a new message in the database.

        :param connection: The SQLite database connection to use.
        :param message: The `email.message.Message` instance
            representing the message to create.
        :return: None.

        """
    message_date_timestamp = datetime.datetime.strptime(
            message['date'], datetime_format_rfc5322)
    row = {
            'created_at': datetime.datetime.utcnow(),
            'message_id': message.message_id,
            'date': message_date_timestamp,
            'sender': message['from'],
            'recipients': message['to'],
            'subject': message['subject'],
            'body': message.get_payload(),
            'mime_type': "text/plain",
            'raw': message.as_string(),
            }
    sql = textwrap.dedent("""\
            INSERT INTO message (
                message_id, created_at, "date", sender, recipients,
                subject, "body", mime_type, "raw"
            )
            VALUES (
                :message_id, :created_at, :date, :sender, :recipients,
                :subject, :body, :mime_type, :raw
            )
            """)
    logger.info(
            "Storing message {id}".format(id=message.message_id))
    cursor = connection.cursor()
    cursor.execute(sql, row)


def retrieve_message(connection, message_id):
    """ Retrieve a message from the database.

        :param connection: The SQLite database connection to use.
        :param message_id: The ‘message-id’ field value of the message.
        :return: An `email.message.Message` instance representing the
            message.

        """
    sql = textwrap.dedent("""\
            SELECT
                message_id,
                raw
            FROM message
            WHERE
                message_id = :message_id
            """)
    sql_params = {
            'message_id': message_id,
            }
    cursor = connection.cursor()
    cursor.execute(sql, sql_params)
    row = cursor.fetchone()

    message = email.message_from_string(row['raw'])

    return message


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
