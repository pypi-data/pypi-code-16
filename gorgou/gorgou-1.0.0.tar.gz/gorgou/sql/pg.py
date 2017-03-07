#!/usr/bin/env python
# -*- coding: utf8 -*-

import psycopg2
import psycopg2.extras
from ..x import json_ext


class Connection(object):
    # BASIC

    def __init__(self, pg_conf_file=None):
        if not pg_conf_file:
            pg_conf_file = 'pg.conf'
        pg_conf = json_ext.load_json(pg_conf_file)
        self.connection = psycopg2.connect(
            host=pg_conf['host'],
            user=pg_conf['user'],
            password=pg_conf['passwd'],
            database=pg_conf['db'],
            port=pg_conf['port'],
            # charset='utf8'
        )
        self.cursor = self.connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor)

    @property
    def cur(self):
        return self.cursor

    @cur.setter
    def cur(self, value):
        self.cursor = value

    @property
    def conn(self):
        return self.connection

    @conn.setter
    def conn(self, value):
        self.connection = value

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def execute(self, *args, **kwargs):
        return self.cur.execute(*args, **kwargs)

    def close(self):
        self.cur.close()
        self.conn.close()

    # ADVANCED
    def get(self, *args, **kwargs):
        self.cur.execute(*args, **kwargs)
        return self.cur.fetchall()

    def get_one(self, *args, **kwargs):
        self.cur.execute(*args, **kwargs)
        return self.cur.fetchone()

    def get_page(self, table, orderBy, where, pageSize, pageNum):
        pager = {}
        pager['pageSize'] = pageSize
        pager['pageNum'] = pageNum
        l = pager['pageSize']
        o = (pager['pageNum'] - 1) * pager['pageSize']
        tmpsql = 'select count(*) as count from ' + table
        if where:
            tmpsql = tmpsql + ' where ' + where
        count = self.get_one(tmpsql)['count']
        pager['pageCount'] = int(
            (count + pager['pageSize'] - 1) / pager['pageSize'])
        if not pager['pageCount']:
            pager['pageCount'] = 1
        tmpsql = 'select * from ' + table
        if where:
            tmpsql = tmpsql + ' where ' + where
        if not orderBy:
            # error
            pass
        tmpsql = tmpsql + ' order by ' + orderBy + ' limit %s offset %s'
        result = self.get(tmpsql, (l, o,))
        return result, pager

    def safe_execute(self, *args, **kwargs):
        try:
            self.cur.execute(*args, **kwargs)
            self.conn.commit()
        except:
            self.conn.rollback()

    def safe_execute_ret_rowcount(self, *args, **kwargs):
        try:
            self.cur.execute(*args, **kwargs)
            self.conn.commit()
            return self.cur.rowcount
        except:
            self.conn.rollback()
            return 0

    def safe_execute_ret_lastrowid(self, *args, **kwargs):
        try:
            self.cur.execute(*args, **kwargs)
            self.conn.commit()
            return self.cur.lastrowid
        except:
            self.conn.rollback()
            return 0
