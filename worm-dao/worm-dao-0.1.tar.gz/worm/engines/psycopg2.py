from __future__ import absolute_import

from psycopg2 import connect, paramstyle  # NOQA
from psycopg2.extras import DictCursor

import psycopg2 as dbapi  # NOQA

from ..adapters.genericsql import GenericSQLAdapter as DefaultAdapter  # NOQA


def initialize_connection(connection):
    connection.cursor_factory = DictCursor
