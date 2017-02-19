# -*- coding: utf-8 -*-

'''
@author: saaj
'''


import os
import sqlite3
import random
import math
import unittest
from datetime import datetime

import MySQLdb as mysql

from .test import mysqlConfig
from .ns import NestedSetsTree
from .compat.mysqldb import Mysqldb as MysqlWrapper
from .compat.sqlite3 import Sqlite3 as SqliteWrapper


def stddev(vector):
  n    = 0
  mean = 0.0
  M2   = 0.0

  for x in vector:
    n    += 1
    delta = x - mean
    mean  = mean + delta / n
    M2    = M2 + delta * (x - mean)

  return math.sqrt(M2 / (n - 1))


Repeat = 8


class TestNsBigMysql(unittest.TestCase):
  
  db      = None
  times   = None
  nodeIds = None
  
  
  def setUp(self):
    self.db = MysqlWrapper(mysql.connect(**mysqlConfig))
    self.db.cursor().execute('SET SESSION query_cache_type = OFF')
    
    self.testee = NestedSetsTree(self.db, 'big', {'number' : 'value'})
    self.testee.columns['nodeId'] = 'node_id'
    
    self.times = []
    
    self.db.begin()
  
  def tearDown(self):
    self.db.rollback()
    
    self._printResults()
  
  def _getIds(self):
    if self.nodeIds is None:
      cursor = self.db.cursor()
      cursor.execute('SELECT node_id FROM big')
      self.nodeIds = tuple(r[0] for r in cursor)
    
    return self.nodeIds
  
  def _printResults(self):
    if self.times:
      times = self.times[1:-1]
      stats = (sum(times), sum(times) / len(times), min(times), max(times), stddev(times))
      print(' | '.join(s.center(8) for s in ('total', 'mean', 'min', 'max', 'stddev')))
      print(' | '.join('{0:.4f}'.format(v).center(8) for v in stats) + '\n')
  
  def testMove(self):
    ids = self._getIds()
    for _ in range(Repeat):
      s = datetime.now()
      while True:
        nodeId   = random.choice(ids)
        parentId = random.choice(ids)
        if nodeId != parentId:
          break
      self.testee.move(nodeId, parentId = parentId)
      self.times.append((datetime.now() - s).total_seconds())
  
  def testGetPath(self):
    ids = self._getIds()
    for _ in range(Repeat):
      s = datetime.now()
      self.testee.getPath(random.choice(ids))
      self.times.append((datetime.now() - s).total_seconds())
    
  def testGetDescendants(self):
    ids = self._getIds()
    for _ in range(Repeat):
      s = datetime.now()
      self.testee.getDescendants(random.choice(ids))
      self.times.append((datetime.now() - s).total_seconds())

  def testValidate(self):
    for _ in range(Repeat):
      s = datetime.now()
      self.testee.validate(True)
      self.times.append((datetime.now() - s).total_seconds())
  
  def testMemorize(self):
    s = datetime.now()
    for c in (None, 8, 128, 384, 1024):
      memoryTree = self.testee.memorize(chunk = c)
      memoryTree.columns['nodeId'] = 'node_id'
      self.assertEqual(self.testee.getRoot(), memoryTree.getRoot())
      self.assertEqual(self.testee.getDescendants(1), memoryTree.getDescendants(1))
      
      print(c, datetime.now() - s)
      s = datetime.now()


class TestNsBigMysqlMemorized(TestNsBigMysql):
  
  def setUp(self):
    super(TestNsBigMysqlMemorized, self).setUp()
    
    self.testee = self.testee.memorize()
    
    self._originalDb = self.db 
    self.db = self.testee._db # memory sqlite 
    self.db.begin()
  
  def tearDown(self):
    self.db.rollback()
    self.db = self._originalDb
    
    super(TestNsBigMysqlMemorized, self).tearDown()


class TestNsBigSqlite(TestNsBigMysql):
  
  def setUp(self):
    self.db = SqliteWrapper(sqlite3.connect(os.path.dirname(__file__) + '/test/fixture/sqlite.db'))
    
    self.testee = NestedSetsTree(self.db, 'big', {'number' : 'value'})
    self.testee.columns['nodeId'] = 'node_id'
    
    self.times = []
    
    self.db.begin()


class TestNsBigSqliteMemorized(TestNsBigSqlite):
  
  def setUp(self):
    super(TestNsBigSqliteMemorized, self).setUp()
    
    self.testee = self.testee.memorize()
    
    self._originalDb = self.db
    self.db = self.testee._db # memory sqlite 
    self.db.begin()
    
  def tearDown(self):
    self.db.rollback()
    self.db = self._originalDb
    
    super(TestNsBigSqliteMemorized, self).tearDown()

