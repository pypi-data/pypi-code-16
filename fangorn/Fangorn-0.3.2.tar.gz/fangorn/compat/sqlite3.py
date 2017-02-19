'''
@author: saaj
'''


from . import Abstract


class Sqlite3(Abstract):

  def __init__(self, connection):
    super(Sqlite3, self).__init__(connection)
    
    self._connection.isolation_level = None
    self._connection.execute('PRAGMA foreign_keys = 1')
  
