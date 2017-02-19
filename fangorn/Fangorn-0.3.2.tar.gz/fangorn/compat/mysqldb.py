'''
@author: saaj
'''


import re

import MySQLdb.cursors as cursors

from . import Abstract


class NamedCursor(cursors.Cursor):

  _placeholderRe = re.compile(':([a-zA-Z]\w+)')


  def execute(self, query, args = None):
    return super(NamedCursor, self).execute(self._placeholderRe.sub('%(\\1)s', query), args)
  

class Mysqldb(Abstract):

  def __init__(self, connection):
    super(Mysqldb, self).__init__(connection)
    
    self._connection.autocommit(True)
    
  def cursor(self):
    return self._connection.cursor(NamedCursor)
  
