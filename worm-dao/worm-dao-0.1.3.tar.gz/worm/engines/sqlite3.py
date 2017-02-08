from __future__ import absolute_import

from sqlite3 import connect, Row, paramstyle  # NOQA
import sqlite3 as dbapi  # NOQA

from ..adapters.genericsql import GenericSQLAdapter as DefaultAdapter  # NOQA


def initialize_connection(connection):
    connection.isolation_level = 'DEFERRED'
    connection.row_factory = Row  # NOQA
