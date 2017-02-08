from __future__ import absolute_import

from psycopg2 import connect, paramstyle  # NOQA
from psycopg2.extras import DictCursor

import psycopg2 as dbapi  # NOQA

from ..adapters.genericsql import GenericSQLAdapter as DefaultAdapter  # NOQA


def initialize_connection(connection):
    connection.cursor_factory = DictCursor


def table_column_names(db, table, schema='public'):
    cur = db.cursor()
    cur.execute('''
        select column_name from information_schema.columns
        where table_schema = %(schema)s and table_name = %(table)s
        ''', {'table': table, 'schema': schema})
    return list(map(lambda x: x[0], cur.fetchall()))


def table_primary_key(db, table, schema='public'):
    cur = db.cursor()
    cur.execute('''
        SELECT column_name
        FROM information_schema.table_constraints
             JOIN information_schema.key_column_usage
             USING (constraint_catalog, constraint_schema, constraint_name,
                table_catalog, table_schema, table_name)
        WHERE constraint_type = 'PRIMARY KEY'
          AND (table_schema, table_name) = (%(schema)s, %(table)s)
        ORDER BY ordinal_position;
        ''', {'table': table, 'schema': schema})

    return list(map(lambda x: x[0], cur.fetchall()))
