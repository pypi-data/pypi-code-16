# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from sqlalchemy import create_engine, text
from past.builtins import basestring
import re
from contextlib import contextmanager


class Dao(object):
    def __init__(self, db, user, password, host='localhost', port=3306, **kwargs):
        self.DB_URI = 'mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8'\
                .format(user=user, password=password, host=host, port=port, db=db)
        kwargs.setdefault('convert_unicode', True)
        kwargs.setdefault('pool_size', 20)
        kwargs.setdefault('max_overflow', 100)
        kwargs.setdefault('pool_recycle', 9)
        kwargs.setdefault('echo', False)
        self._engine = create_engine(self.DB_URI, **kwargs)

    def close(self):
        self._conn.close()

    @property
    def engine(self):
        return self._engine

    @contextmanager
    def conn(self):
        conn = self._engine.connect()
        try:
            yield conn
        finally:
            conn.close()

    def db_query(self, sql_txt):
        with self.conn() as conn:
            result = conn.execute(text(sql_txt))
            rows = result.fetchall()
            return rows

    def db_change(self, sql_txt):
        with self.conn() as conn:
            result = conn.execute(text(sql_txt))
            return result

    def _format_field(self, field):
        return '`%s`' % field

    def _format_value(self, val):
        if val is None:
            return 'NULL'
        elif isinstance(val, basestring):
            val = re.sub('\'', '\\\'', val)
            val = re.sub(':', '\:', val)
            return '\'%s\'' % val
        else:
            return str(val)

    def insert_object(self, table, obj):
        fields = ','.join([self._format_field(k) for k in obj.keys()])
        values = ','.join([self._format_value(v) for v in obj.values()])

        sql = 'insert into %s(%s) values(%s)' % (table, fields, values)
        return self.db_change(sql)

    def get_object(self, table, where):
        wheres = ['%s=%s' % (self._format_field(k), self._format_value(v))
            for k, v in where.items()]
        wheres = ' and '.join(wheres)
        sql = 'select * from %s where %s' % (table, wheres)
        print(sql)
        return self.db_query(sql)

    def update_object(self, obj, where, table):
        assigns = ['%s=%s' % (self._format_field(k), self._format_value(v))
            for k, v in obj.items()]
        assigns = ','.join(assigns)
        wheres = ['%s=%s' % (self._format_field(k), self._format_value(v))
            for k, v in where.items()]
        wheres = ' and '.join(wheres)
        sql = 'update %s set %s where %s' % (table, assigns, wheres)
        print(sql)
        return self.db_change(sql)

    def delete_object(self, val, field, table):
        sql = 'delete from %s where %s=%s' % (table, self._format_field(field),
            self._format_value(val))
        return self.db_change(sql)

    def get_all_objects(self, table):
        sql = 'select * from %s' % table
        return self.db_query(sql)

    def delete_all_objects(self, table):
        return self.db_change('truncate %s' % table)

    def is_exist(self, item, table):
        wheres = ['%s=%s' % (self._format_field(k), self._format_value(v))
            for k, v in item.items()]
        wheres = ','.join(wheres)
        sql = 'select count(*) from %s where %s' % (table, wheres)
        result = self.db_query(sql)
        if result[0][0] > 0:
            return True
        return False
