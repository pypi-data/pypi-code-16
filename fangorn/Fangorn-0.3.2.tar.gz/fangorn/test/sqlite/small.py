# -*- coding: utf-8 -*-
'''
@author: saaj
'''


import os
import sqlite3

from ..small import TestNsSmall
from ...ns import NestedSetsTree
from ...compat.sqlite3 import Sqlite3 as SqliteWrapper


class TestNsSmallSqlite(TestNsSmall):
  
  def setUp(self):
    self.db = SqliteWrapper(sqlite3.connect(os.path.dirname(__file__) + '/../fixture/sqlite.db'))
    
    super(TestNsSmallSqlite, self).setUp()
    
    self.testee = NestedSetsTree(self.db, 'small', ('name',))
    self.testee.columns['nodeId'] = 'node_id'
  

class TestNsSmallSqliteMemorized(TestNsSmallSqlite):
  
  def setUp(self):
    super(TestNsSmallSqliteMemorized, self).setUp()
    
    self.testee = self.testee.memorize()
    
    self._originalDb = self.db
    self.db = self.testee._db # memory sqlite 
    self.db.begin()
    
  def tearDown(self):
    self.db.rollback()
    self.db = self._originalDb
    
    super(TestNsSmallSqliteMemorized, self).tearDown()

