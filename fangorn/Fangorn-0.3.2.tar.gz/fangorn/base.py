'''
@author: saaj
'''


class NotFoundError(Exception):
  ''''Raised when node was not found'''
  
class IntegrityError(Exception):
  '''Raised when tree is broken'''


class Tree(object):
  
  _table = None
  '''Name of tree-holding table'''
  
  _db  = None
  '''Database connection object'''
  
  columns = None
  '''Tree table columns'''
  
  valueColumns = None
  '''Non-system tree table columns'''
  
  
  def __init__(self, db, table, valueColumns = None):
    self._table = table
    self._db    = db
   
    if isinstance(valueColumns, dict):
      self.valueColumns = valueColumns
    elif valueColumns:
      self.valueColumns = dict(zip(valueColumns, valueColumns))
    else:
      self.valueColumns = {}
    
    self.columns = dict(self.valueColumns, **{
      'nodeId'   : '{0}_id'.format(table),
      'parentId' : 'parent_id',
      'left'     : 'l',
      'right'    : 'r'
    })
    
  def add(self, values, parentId = None, prevId = None):
    raise NotImplementedError # pragma: no cover

  def edit(self, id, values):
    raise NotImplementedError # pragma: no cover

  def remove(self, id):
    raise NotImplementedError # pragma: no cover

  def move(self, id, parentId = None, prevId = None):
    raise NotImplementedError # pragma: no cover 
  
  def getRoot(self):
    raise NotImplementedError # pragma: no cover
  
  def getNode(self, id):
    raise NotImplementedError # pragma: no cover
  
  def getParent(self, id):
    raise NotImplementedError # pragma: no cover
  
  def getNext(self, id):
    raise NotImplementedError # pragma: no cover
  
  def getPrevious(self, id):
    raise NotImplementedError # pragma: no cover
  
  def getPath(self, id):
    raise NotImplementedError # pragma: no cover
  
  def getChildren(self, id):
    raise NotImplementedError # pragma: no cover
  
  def getDescendants(self, id):
    raise NotImplementedError # pragma: no cover
  
  def isDescendantOf(self, parentId, descendantId):
    raise NotImplementedError # pragma: no cover
  
  def isLeaf(self, id):
    raise NotImplementedError # pragma: no cover
  
  def validate(self):
    raise NotImplementedError # pragma: no cover
  
  def memorize(self, chunk = None, index = True):
    raise NotImplementedError # pragma: no cover

