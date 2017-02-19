'''
@author: saaj
'''


from __future__ import division

import sqlite3

from .compat.sqlite3 import Sqlite3 as Wrapper
from .base import Tree, NotFoundError, IntegrityError


class NestedSetsTree(Tree):

  _validator = None
  '''Markup validator'''


  def __init__(self, db, table, valueColumns = None):
    super(NestedSetsTree, self).__init__(db, table, valueColumns)

    self._validator = NestedSetsValidator(self)

  def _getMeta(self, prefix = ''):
    return dict(self.columns, **{
      'table'  : self._table,
      'fields' : ','.join('{0}{1}'.format(prefix, f) for f in self.columns.values())
    })

  def _nameColumns(self, row):
    return dict(zip(self.columns.keys(), row))

  def _updateMarkup(self, prev, width):
    meta   = self._getMeta()
    cursor = self._db.cursor()
    values = dict(prev = prev, width = width)

    sql = '''
      UPDATE {table}
      SET {left} = {left} + :width
      WHERE {left} > :prev
    '''
    cursor.execute(sql.format(**meta), values)

    sql = '''
      UPDATE {table}
      SET {right} = {right} + :width
      WHERE {right} > :prev
    '''
    cursor.execute(sql.format(**meta), values)

  def add(self, values, parentId = None, prevId = None):
    self._db.begin()
    try:
      # if neither then it's root adding
      if parentId or prevId:
        if prevId:
          target = self.getNode(prevId)
          if target['parentId'] is None:
            raise IntegrityError('Cannot add node behind root')

          parentId = target['parentId']
          prev     = target['right']
        else:
          target = self.getNode(parentId)
          prev   = target['left']

        self._updateMarkup(prev, 2)
      else:
        prev = 0

      values['parentId'] = parentId
      values['left']     = prev + 1;
      values['right']    = prev + 2;

      sql = '''
        INSERT INTO {table}({fields})
        VALUES({values})
      '''

      meta           = self._getMeta()
      meta['fields'] = ','.join(v for k, v in self.columns.items() if k in values)
      meta['values'] = ','.join(':{0}'.format(k) for k in self.columns.keys() if k in values)

      cursor = self._db.cursor()
      cursor.execute(sql.format(**meta), values)

      self._db.commit()

      return cursor.lastrowid
    except:
      self._db.rollback()
      raise

  def edit(self, id, values):
    sql = '''
      UPDATE {table}
      SET {values}
      WHERE {nodeId} = :id
    '''

    meta           = self._getMeta()
    meta['values'] = ','.join('{0} = :{1}'.format(v, k)
      for k, v in self.valueColumns.items() if k in values)

    self._db.cursor().execute(sql.format(**meta), dict(values, id = id))

  def remove(self, id):
    self._db.begin()
    try:
      target = self.getNode(id)

      sql = '''
        DELETE FROM {table}
        WHERE {left} BETWEEN :left AND :right
      '''
      self._db.cursor().execute(sql.format(**self._getMeta()), target)

      self._updateMarkup(target['right'], target['left'] - target['right'] - 1)

      self._db.commit()
    except:
      self._db.rollback()
      raise

  def move(self, id, parentId = None, prevId = None):
    self._db.begin()
    try:
      if prevId:
        if prevId == id:
          return
        target   = self.getNode(prevId)
        parentId = target['parentId']
        prev     = target['right']
      else:
        target = self.getNode(parentId)
        prev   = target['left']

      if parentId == id:
        raise IntegrityError('Cannot move node into self')
      if self.isDescendantOf(id, parentId):
        raise IntegrityError('Cannot move node under its own descendant')

      node = self.getNode(id)
      # shift nodes on the width of moving subtree, like in add()
      self._updateMarkup(prev, node['right'] - node['left'] + 1)

      cursor = self._db.cursor()
      meta   = self._getMeta()

      sql = '''
        UPDATE {table}
        SET {parentId} = :parentId
        WHERE {nodeId} = :id
      '''
      cursor.execute(sql.format(**meta), dict(id = id, parentId = parentId))

      # re-fetch node and prev value since could be changed
      node = self.getNode(id)
      if prevId:
        target = self.getNode(prevId)
        prev   = target['right']
      else:
        target = self.getNode(parentId)
        prev   = target['left']

      sql = '''
        UPDATE {table}
        SET {right} = {right} + :offset,
            {left}  = {left} + :offset
        WHERE {left} > :left - 1 AND {right} < :right + 1
      '''
      cursor.execute(sql.format(**meta), dict(node, offset = prev - node['left'] + 1))

      # shift nodes on the width of moving subtree, like in remove()
      self._updateMarkup(node['right'], node['left'] - node['right'] - 1)

      self._db.commit()
    except:
      self._db.rollback()
      raise

  def getRoot(self):
    sql = '''
      SELECT {fields}
      FROM {table}
      WHERE {left} = 1
    '''

    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta()))
    result = cursor.fetchone()

    if not result:
      raise NotFoundError('No root node')
    else:
      return self._nameColumns(result)

  def getNode(self, id):
    sql = '''
      SELECT {fields}
      FROM {table}
      WHERE {nodeId} = :id
    '''

    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta()), {'id' : id})
    result = cursor.fetchone()

    if not result:
      raise NotFoundError('No node with id:{0}'.format(id))
    else:
      return self._nameColumns(result)

  def getParent(self, id):
    sql = '''
      SELECT {fields}
      FROM {table} n
      JOIN {table} p ON n.{parentId} = p.{nodeId}
      WHERE n.{nodeId} = :id
    '''

    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta('p.')), {'id' : id})
    result = cursor.fetchone()

    if not result:
      raise NotFoundError('No parent node for id:{0}'.format(id))
    else:
      return self._nameColumns(result)

  def getNext(self, id):
    sql = '''
      SELECT {fields}
      FROM {table} n
      JOIN {table} s ON n.{right} + 1 = s.{left} AND n.{parentId} = s.{parentId}
      WHERE n.{nodeId} = :id
    '''

    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta('s.')), {'id' : id})
    result = cursor.fetchone()

    if not result:
      raise NotFoundError('No right sibling node for id:{0}'.format(id))
    else:
      return self._nameColumns(result)

  def getPrevious(self, id):
    sql = '''
      SELECT {fields}
      FROM {table} n
      JOIN {table} s ON n.{left} - 1 = s.{right} AND n.{parentId} = s.{parentId}
      WHERE n.{nodeId} = :id
    '''

    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta('s.')), {'id' : id})
    result = cursor.fetchone()

    if not result:
      raise NotFoundError('No left sibling node for id:{0}'.format(id))
    else:
      return self._nameColumns(result)

  def getPath(self, id):
    sql = '''
      SELECT {fields}
      FROM {table} n
      JOIN {table} a ON a.{left} <= n.{left} AND a.{right} >= n.{right}
      WHERE n.{nodeId} = :id
      ORDER BY a.{left} ASC
    '''

    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta('a.')), {'id' : id})

    return list(map(self._nameColumns, cursor))

  def getChildren(self, id):
    sql = '''
      SELECT {fields}
      FROM {table} n
      JOIN {table} c ON n.{nodeId} = c.{parentId}
      WHERE n.{nodeId} = :id
      ORDER BY c.{left} ASC
    '''

    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta('c.')), {'id' : id})

    return list(map(self._nameColumns, cursor))

  def getDescendants(self, id):
    sql = '''
      SELECT {fields}
      FROM {table} d
      JOIN {table} n ON d.{left} BETWEEN n.{left} + 1 AND n.{right} - 1
      WHERE n.{nodeId} = :id
      ORDER BY d.{left} ASC
    '''

    cursor = self._db.cursor()
    cursor.execute(sql.format(**self._getMeta('d.')), {'id' : id})

    return list(map(self._nameColumns, cursor))

  def isDescendantOf(self, parentId, descendantId):
    parent     = self.getNode(parentId)
    descendant = self.getNode(descendantId)

    return parent['left'] < descendant['left'] and parent['right'] > descendant['right']

  def isLeaf(self, id):
    node = self.getNode(id)

    return node['right'] - node['left'] == 1

  def validate(self, edges = False):
    self._validator.validate(edges)

  def memorize(self, chunk = 4096, index = True):
    connection   = Wrapper(sqlite3.connect(':memory:'))
    targetCursor = connection.cursor()
    meta         = self._getMeta()

    sql = '''
      CREATE TABLE {table} (
        {nodeId}   INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        {parentId} INTEGER DEFAULT NULL REFERENCES {table}({nodeId})
          ON DELETE CASCADE ON UPDATE CASCADE,
        {left}     INTEGER NOT NULL,
        {right}    INTEGER NOT NULL
        {valueColumns}
      )
    '''
    valueColumns = ''
    if self.valueColumns:
      root         = self.getRoot()
      valueColumns = ', ' + ','.join(
        '{0} {1}'.format(v, 'INTEGER' if isinstance(root[k], int) else 'TEXT')
        for k, v in self.valueColumns.items()
      )
    sql = sql.format(**dict(meta, valueColumns = valueColumns))

    targetCursor.execute(sql)

    meta['values'] = ','.join(':{0}'.format(k) for k in self.columns.keys())
    def insert(values):
      sql = '''
        INSERT INTO {table}({fields})
        VALUES({values})
      '''
      targetCursor.executemany(sql.format(**meta), values)
      return targetCursor.rowcount

    sourceCursor = self._db.cursor()
    if chunk:
      index    = 0
      inserted = 0
      while not index or inserted > 0:
        sql = '''
          SELECT {fields}
          FROM {table}
          LIMIT {offset}, {limit}
        '''
        sourceCursor.execute(sql.format(offset = chunk * index, limit = chunk, **meta))
        inserted = insert(sourceCursor)
        index += 1
    else:
      sql = '''
        SELECT {fields}
        FROM {table}
      '''
      sourceCursor.execute(sql.format(**meta))
      insert(sourceCursor)

    if index:
      targetCursor.execute('CREATE INDEX {left} ON {table}({left})'.format(**meta))
      targetCursor.execute('CREATE INDEX {right} ON {table}({right})'.format(**meta))
      targetCursor.execute('CREATE INDEX {parentId} ON {table}({parentId})'.format(**meta))

    memorized         = self.__class__(connection, self._table, self.valueColumns)
    memorized.columns = self.columns

    return memorized


class NestedSetsValidator(object):

  _tree  = None
  '''Nested sets tree instance'''


  def __init__(self, tree):
    self._tree = tree

  def _getFirst(self, rows):
    return tuple(r[0] for r in rows)

  def _getNodeCount(self):
    sql = '''
      SELECT COUNT(*)
      FROM {table}
    '''
    cursor = self._tree._db.cursor()
    cursor.execute(sql.format(**self._tree._getMeta()))
    return cursor.fetchone()[0]

  def _validateLeftLessThanRight(self):
    sql = '''
      SELECT {nodeId}
      FROM {table}
      WHERE {left} >= {right}
    '''
    cursor = self._tree._db.cursor()
    cursor.execute(sql.format(**self._tree._getMeta()))
    broken = cursor.fetchall()
    if broken:
      raise IntegrityError('Left must always be less than right: {0}'.format(
        self._getFirst(broken)))

  def _validateNoLoops(self):
    sql = '''
      SELECT {nodeId}
      FROM {table}
      WHERE {parentId} = {nodeId}
    '''
    cursor = self._tree._db.cursor()
    cursor.execute(sql.format(**self._tree._getMeta()))
    broken = cursor.fetchall()
    if broken:
      raise IntegrityError('Tree must have no loops: {0}'.format(self._getFirst(broken)))

  def _validateMinMax(self):
    sql = '''
      SELECT MIN({left}), MAX({right}), COUNT(*)
      FROM {table}
    '''
    cursor = self._tree._db.cursor()
    cursor.execute(sql.format(**self._tree._getMeta()))
    stats = cursor.fetchone()
    if stats[0] != 1:
      raise IntegrityError('Min left must always be 1')
    if stats[1] / 2 != stats[2]:
      raise IntegrityError('Max right must always be number of nodes / 2')

  def _validateRoot(self):
    sql = '''
      SELECT MIN({left}), MAX({right})
      FROM {table}
    '''
    cursor = self._tree._db.cursor()
    cursor.execute(sql.format(**self._tree._getMeta()))
    stats = cursor.fetchone()

    sql = '''
      SELECT {parentId}
      FROM {table}
      WHERE {left} = :left AND {right} = :right
    '''
    cursor = self._tree._db.cursor()
    cursor.execute(sql.format(**self._tree._getMeta()), dict(left = stats[0], right = stats[1]))
    stats = cursor.fetchone()
    if not stats:
      raise IntegrityError('Tree must have one root')
    elif stats[0] is not None:
      raise IntegrityError('Parent of root must be none')

  def _validateOddDifference(self):
    sql = '''
      SELECT {nodeId}
      FROM {table}
      WHERE ({right} - {left}) %  2 != 1
    '''
    cursor = self._tree._db.cursor()
    cursor.execute(sql.format(**self._tree._getMeta()))
    broken = cursor.fetchall()
    if broken:
      raise IntegrityError('Right - left must always be odd: {0}'.format(self._getFirst(broken)))

  def _validateUniqueMarkup(self):
    sql = '''
      SELECT GROUP_CONCAT(a.{nodeId}), a.m
      FROM (
          SELECT {nodeId}, {left} m
          FROM {table}
        UNION ALL
          SELECT {nodeId}, {right} m
          FROM {table}
      ) a
      GROUP BY a.m
      HAVING COUNT(*) != 1
    '''
    cursor = self._tree._db.cursor()
    cursor.execute(sql.format(**self._tree._getMeta()))
    broken = cursor.fetchall()
    if broken:
      raise IntegrityError('Markup must be unique: {0}'.format(tuple(broken)))

  def _validateAdjacencyListEdgeMatch(self):
    # This query is slow. About few minutes for 40K-row tree.
    # Note that since MySQL 5.7 even with ONLY_FULL_GROUP_BY disabled
    # is not backward-compatible in sense of returning first record per group
    # like in this answer, http://stackoverflow.com/a/2739825/2072035.
    # Because SQLite doesn't support ordering in GROUP_CONCAT there are
    # two queries.
    try:
      self._tree._db.cursor().execute('SELECT sqlite_version()')
      # Note that SQLite reverses the order of joined parent table
      # so it has ASC sorting to produce the same GROUP BY result as DESC
      # in MySQL < 5.7.
      sql = '''
        SELECT a.nid, a.pid
        FROM (
            SELECT n.{nodeId} `nid`, p.{nodeId} `pid`
            FROM {table} n
            LEFT JOIN (
              SELECT {nodeId}, {left}, {right}
              FROM {table}
              ORDER BY {left} ASC
            ) p ON p.{left} < n.{left} AND p.{right} > n.{right}
            GROUP BY n.{nodeId}
          UNION ALL
            SELECT {nodeId} nid, {parentId} pid
            FROM {table}
        ) a
        GROUP BY a.nid, a.pid
        HAVING COUNT(*) != 2
      '''
    except Exception:
      # MySQL query compatible with both 5.7+ and previous versions.
      sql = '''
        SELECT a.nid, a.pid
        FROM (
            SELECT n.{nodeId} `nid`,
              CAST(SUBSTRING_INDEX(GROUP_CONCAT(p.{nodeId} ORDER BY p.{left} DESC), ',', 1)
                AS UNSIGNED) `pid`
            FROM {table} n
            LEFT JOIN {table} p ON p.{left} < n.{left} AND p.{right} > n.{right}
            GROUP BY n.{nodeId}
          UNION ALL
            SELECT {nodeId} `nid`, {parentId} `pid`
            FROM {table}
        ) a
        GROUP BY a.nid, a.pid
        HAVING COUNT(*) != 2
      '''

    cursor = self._tree._db.cursor()
    cursor.execute(sql.format(**self._tree._getMeta()))
    broken = tuple(cursor.fetchall())
    if broken:
      raise IntegrityError('Adjacency list edges do not match '
        'nested sets edges: {0}'.format(broken))

  def validate(self, edges):
    if not self._getNodeCount():
      return

    [f() for f in (self._validateLeftLessThanRight, self._validateNoLoops, self._validateMinMax,
      self._validateRoot, self._validateOddDifference, self._validateUniqueMarkup)]

    if edges:
      self._validateAdjacencyListEdgeMatch()

