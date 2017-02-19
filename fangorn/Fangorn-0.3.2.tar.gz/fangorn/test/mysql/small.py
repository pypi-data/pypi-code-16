# -*- coding: utf-8 -*-
'''
@author: saaj
'''


from . import mysql
from .. import mysqlConfig
from ..small import TestNsSmall
from ...ns import NestedSetsTree
from ...compat.mysqldb import Mysqldb as MysqlWrapper


class TestNsSmallMysql(TestNsSmall):
  
  def setUp(self):
    self.db = MysqlWrapper(mysql.connect(**mysqlConfig))
    
    super(TestNsSmallMysql, self).setUp()
    
    self.testee = NestedSetsTree(self.db, 'small', ('name',))
    self.testee.columns['nodeId'] = 'node_id'
    
  def tearDown(self):
    super(TestNsSmallMysql, self).tearDown()
    
    self.db._connection.close()
  

class TestNsSmallMysqlMemorized(TestNsSmallMysql):
  
  def setUp(self):
    super(TestNsSmallMysqlMemorized, self).setUp()
    
    self.testee = self.testee.memorize()
    
    self._originalDb = self.db 
    self.db = self.testee._db # memory sqlite 
    self.db.begin()
    
  def tearDown(self):
    self.db.rollback()
    self.db = self._originalDb
    
    super(TestNsSmallMysqlMemorized, self).tearDown()

