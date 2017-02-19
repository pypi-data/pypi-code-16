# -*- coding: utf-8 -*-

'''
@author: saaj
'''


import os
import sqlite3

from ..large import TestNsLarge
from ...ns import NestedSetsTree
from ...compat.sqlite3 import Sqlite3 as SqliteWrapper


class TestNsLargeSqlite(TestNsLarge):
  
  def setUp(self):
    self.db = SqliteWrapper(sqlite3.connect(os.path.dirname(__file__) + '/../fixture/sqlite.db'))
    
    super(TestNsLargeSqlite, self).setUp()
    
    self.testee = NestedSetsTree(self.db, 'large', {'number' : 'value'})
    self.testee.columns['nodeId'] = 'node_id'


class TestNsLargeSqliteMemorized(TestNsLargeSqlite):
  
  def setUp(self):
    super(TestNsLargeSqliteMemorized, self).setUp()
    
    self.testee = self.testee.memorize()
    
    self._originalDb = self.db
    self.db = self.testee._db # memory sqlite 
    self.db.begin()
    
  def tearDown(self):
    self.db.rollback()
    self.db = self._originalDb
    
    super(TestNsLargeSqliteMemorized, self).tearDown()

