#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 12 May 08:33:24 2011

"""Some utilities shared by many of the databases.
"""

import os
import tarfile


class null(object):
  """A look-alike stream that discards the input"""

  def write(self, s):
    """Writes contents of string ``s`` on this stream"""

    pass

  def flush(self):
    """Flushes the stream"""

    pass


def apsw_is_available():
  """Checks lock-ability for SQLite on the current file system"""

  try:
    import apsw #another python sqlite wrapper (maybe supports URIs)
  except ImportError:
    return False

  # if you got here, apsw is available, check we have matching versions w.r.t
  # the sqlit3 module
  import sqlite3

  if apsw.sqlitelibversion() != sqlite3.sqlite_version:
    return False

  # if you get to this point, all seems OK
  return True


class SQLiteConnector(object):
  '''An object that handles the connection to SQLite databases.

  Parameters:

    filename (str): The name of the file containing the SQLite database

    readonly (bool): Should I try and open the database in read-only mode?

    lock (str): Any vfs name as output by apsw.vfsnames()

  '''

  @staticmethod
  def filesystem_is_lockable(database):
    """Checks if the filesystem is lockable"""
    from sqlite3 import connect

    old = os.path.exists(database) #memorize if the database was already there
    conn = connect(database)

    retval = True
    try:
      conn.execute('PRAGMA synchronous = OFF')
    except Exception:
      retval = False
    finally:
      if not old and os.path.exists(database): os.unlink(database)

    return retval

  APSW_IS_AVAILABLE = apsw_is_available()


  def __init__(self, filename, readonly=False, lock=None):

    self.readonly = readonly
    self.vfs = lock
    self.filename = filename
    self.lockable = SQLiteConnector.filesystem_is_lockable(self.filename)

    if (self.readonly or (self.vfs is not None)) and \
        not self.APSW_IS_AVAILABLE and not self.lockable:
        import warnings
        warnings.warn('Got a request for an SQLite connection using APSW, but I cannot find an sqlite3-compatible installed version of that module (or the module is not installed at all). Furthermore, the place where the database is sitting ("%s") is on a filesystem that does **not** seem to support locks. I\'m returning a stock connection and hopping for the best.' % (filename,))


  def __call__(self):

    from sqlite3 import connect

    if (self.readonly or (self.vfs is not None)) and self.APSW_IS_AVAILABLE:
      # and not self.lockable
      import apsw
      if self.readonly: flags = apsw.SQLITE_OPEN_READONLY #1
      else: flags = apsw.SQLITE_OPEN_READWRITE | apsw.SQLITE_OPEN_CREATE #2|4
      apsw_con = apsw.Connection(self.filename, vfs=self.vfs, flags=flags)
      return connect(apsw_con)

    return connect(self.filename, check_same_thread=False)


  def create_engine(self, echo=False):
    """Returns an SQLAlchemy engine"""

    from sqlalchemy import create_engine
    from sqlalchemy.pool import NullPool
    return create_engine('sqlite://', creator=self, echo=echo, poolclass=NullPool)


  def session(self, echo=False):
    """Returns an SQLAlchemy session"""

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=self.create_engine(echo))
    return Session()


def session(dbtype, dbfile, echo=False):
  """Creates a session to an SQLite database"""

  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker

  url = connection_string(dbtype, dbfile)
  engine = create_engine(url, echo=echo)
  Session = sessionmaker(bind=engine)
  return Session()

def session_try_readonly(dbtype, dbfile, echo=False):
  """Creates a read-only session to an SQLite database.

  If read-only sessions are not supported by the underlying sqlite3 python DB
  driver, then a normal session is returned. A warning is emitted in case the
  underlying filesystem does not support locking properly.


  Raises:

    NotImplementedError: if the dbtype is not supported.

  """

  if dbtype != 'sqlite':
    raise NotImplementedError("Read-only sessions are only currently supported for SQLite databases")

  connector = SQLiteConnector(dbfile, readonly=True, lock='unix-none')
  return connector.session(echo=echo)


def create_engine_try_nolock(dbtype, dbfile, echo=False):
  """Creates an engine connected to an SQLite database with no locks.

  If engines without locks are not supported by the underlying sqlite3 python
  DB driver, then a normal engine is returned. A warning is emitted if the
  underlying filesystem does not support locking properly in this case.


  Raises:

    NotImplementedError: if the dbtype is not supported.

  """

  if dbtype != 'sqlite':
    raise NotImplementedError("Unlocked engines are only currently supported for SQLite databases")

  connector = SQLiteConnector(dbfile, lock='unix-none')
  return connector.create_engine(echo=echo)


def session_try_nolock(dbtype, dbfile, echo=False):
  """Creates a session to an SQLite database with no locks.

  If sessions without locks are not supported by the underlying sqlite3 python
  DB driver, then a normal session is returned. A warning is emitted if the
  underlying filesystem does not support locking properly in this case.


  Raises:

    NotImplementedError: if the dbtype is not supported.

  """

  if dbtype != 'sqlite':
    raise NotImplementedError("Unlocked sessions are only currently supported for SQLite databases")

  connector = SQLiteConnector(dbfile, lock='unix-none')
  return connector.session(echo=echo)


def connection_string(dbtype, dbfile, opts={}):
  """Returns a connection string for supported platforms

  Parameters:

    dbtype (str): The type of database (only ``sqlite`` is supported for the
      time being)

    dbfile (str): The location of the file to be used

  """

  from sqlalchemy.engine.url import URL
  return URL(dbtype, database=dbfile)


resolved = lambda x: os.path.realpath(os.path.abspath(x))


def safe_tarmembers(archive):
  """Gets a list of safe members to extract from a tar archive

  This list excludes:

    * Full paths outside the destination sandbox
    * Symbolic or hard links to outside the destination sandbox

  Code came from a StackOverflow answer:
  http://stackoverflow.com/questions/10060069/safely-extract-zip-or-tar-using-python

  Deploy it like this:

  .. code-block:: python

     ar = tarfile.open("foo.tar")
     ar.extractall(path="./sandbox", members=safe_tarmembers(ar))
     ar.close()


  Parameters:

    archive (tarfile.TarFile): An opened tar file for reading


  Returns:

    list: A list of :py:class:`tarfile.TarInfo` objects that satisfy the
    security criteria imposed by this function, as denoted above.

  """

  def _badpath(path, base):
    # os.path.join will ignore base if path is absolute
    return not resolved(os.path.join(base,path)).startswith(base)

  def _badlink(info, base):
    # Links are interpreted relative to the directory containing the link
    tip = resolved(os.path.join(base, os.path.dirname(info.name)))
    return badpath(info.linkname, base=tip)

  base = resolved(".")

  for finfo in archive:
    if _badpath(finfo.name, base):
      print("not extracting `%s': illegal path" % (finfo.name,))
    elif finfo.islnk() and _badlink(finfo, base):
      print("not extracting `%s': hard link to `%s'" % \
          (finfo.name, finfo.linkname))
    elif finfo.issym() and _badlink(finfo, base):
      print("not extracting `%s': symlink to `%s'" % \
          (finfo.name, finfo.linkname))
    else:
      yield finfo
