# -*- coding: utf-8 -*-

'''
@author: saaj
'''


from . import mysql
from .. import mysqlConfig
from ..large import TestNsLarge
from ...ns import NestedSetsTree
from ...compat.mysqldb import Mysqldb as MysqlWrapper


class TestNsLargeMysql(TestNsLarge):
  
  def setUp(self):
    self.db = MysqlWrapper(mysql.connect(**mysqlConfig))
    
    super(TestNsLargeMysql, self).setUp()
    self.testee = NestedSetsTree(self.db, 'large', {'number' : 'value'})
    self.testee.columns['nodeId'] = 'node_id'
    
  def tearDown(self):
    super(TestNsLargeMysql, self).tearDown()
    
    self.db._connection.close()
    

class TestNsLargeMysqlMemorized(TestNsLargeMysql):
  
  def setUp(self):
    super(TestNsLargeMysqlMemorized, self).setUp()
    
    self.testee = self.testee.memorize()
    
    self._originalDb = self.db 
    self.db = self.testee._db # memory sqlite 
    self.db.begin()
    
  def tearDown(self):
    self.db.rollback()
    self.db = self._originalDb
    
    super(TestNsLargeMysqlMemorized, self).tearDown()

