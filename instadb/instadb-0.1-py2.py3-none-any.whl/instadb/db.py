import psycopg2 as pg
from psycopg2 import extras
import pandas as pd
import pandas.io.sql as psql
import os
from urlparse import urlparse
import logging

class Db():

  def __init__(self, url=None, env=None, connect_timeout=5):
    self.url = url
    self.env = env
    self.connect_timeout = connect_timeout
    self._init_conn()

  def _init_conn(self):
    if not self.url:
      self._set_url_from_env()

    print self.url
    db_url = urlparse(self.url)
    self.conn = pg.connect(connection_factory=extras.MinTimeLoggingConnection,
                           database=db_url.path[1:],
                           user=db_url.username,
                           password=db_url.password,
                           host=db_url.hostname,
                           port=db_url.port,
                           connect_timeout=self.connect_timeout)

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    self.conn.initialize(logger)
    self.conn.autocommit = True
    self.cur = self.conn.cursor()

  def _set_url_from_env(self):
    self.url = os.environ.get(self.env, None)
    if not self.url:
      raise Exception("ENV variable %s is missing" % self.env)

  def to_dataframe(self, query=None, **kwargs):
    filename = kwargs.pop("filename", __file__)
    query = (""" /*%s*/ """ % filename) + query
    df = psql.read_sql(sql=query, con=self.conn, **kwargs)
    return df
