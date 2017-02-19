'''
@author: saaj
'''


class Abstract(object):
  '''Abstract wrapper for connection object. Declares the API subset Fangorn uses.
  Constructor must enable auto-commit mode on given connection. Cursors must implement 
  'named' DB-API paramstyle. Transaction control methods are recommended to implement 
  nested transaction support. However the test suite requires nested transactions to run.'''

  _connection       = None
  _transactionLevel = 0


  def __init__(self, connection):
    self._connection = connection

  def cursor(self):
    return self._connection.cursor()
  
  def begin(self):
    if self._transactionLevel == 0:
      self.cursor().execute('BEGIN')
    else:
      self.cursor().execute('SAVEPOINT LEVEL{0}'.format(self._transactionLevel))

    self._transactionLevel += 1

  def commit(self):
    self._transactionLevel -= 1

    if self._transactionLevel == 0:
      self.cursor().execute('COMMIT')
    else:
      self.cursor().execute('RELEASE SAVEPOINT LEVEL{0}'.format(self._transactionLevel))

  def rollback(self):
    self._transactionLevel -= 1

    if self._transactionLevel == 0:
      self.cursor().execute('ROLLBACK')
    else:
      self.cursor().execute('ROLLBACK TO SAVEPOINT LEVEL{0}'.format(self._transactionLevel))

