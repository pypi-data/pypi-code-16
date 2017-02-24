# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
# This module is part of the package GTW.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.File_Session
#
# Purpose
#    Session backend which stores the information in a file on the disk
#
# Revision Dates
#    25-Jan-2010 (MG) Creation
#    19-Feb-2010 (MG) Moved from `GTW.Tornado` into `GTW`
#    10-Mar-2011 (CT) Property `_file_name` renamed to `file_name`,
#                     `exists` and `file_name` changed to use factored method
#                     `_file_name` (previously, `exists` and `_file_name`
#                     differed erroneously)
#    11-May-2011 (MG) `file_name` changed from `Once_Property` to `property`
#                     (because `_sid` can changed during the lifetime of the
#                     session object)
#     5-Apr-2012 (CT) Sort alphabetically
#    26-Apr-2012 (CT) Add debug output to `_load`, split its exception handler
#    19-Aug-2012 (MG) Add locking of session file
#    23-Aug-2012 (CT) Add missing import for `fcntl`
#    24-Aug-2012 (MG) Import for `fcntl` moved to `posix` part
#     2-May-2013 (CT) Call `fchmod` to clear permissions for `group` and `other`
#    14-Sep-2013 (MG) Move `fchmod` call to posix function
#    11-Dec-2014 (CT) Remove obsolete code from `remove`
#    11-Dec-2014 (CT) Change `save` to skip/remove empty sessions
#    29-Oct-2015 (CT) Improve Python 3 compatibility
#    ««revision-date»»···
#--

from   __future__               import print_function

from   _GTW                     import GTW
from   _TFL.pyk                 import pyk
from   _TFL._Meta.Once_Property import Once_Property

import _GTW.Session
import os
import stat
import sys

cPickle = pyk.pickle

class Lock_Failed (Exception) :
    pass
# end class Lock_Failed

if os.name == "nt" :
    import win32file
    import win32con
    import pywintypes
    __overlapped = pywintypes.OVERLAPPED ()

    def _lock_impl (file, exclusive, nonblocking) :
        if exclusive :
            flags = win32con.LOCKFILE_EXCLUSIVE_LOCK
        else :
            flags = 0
        if nonblocking :
            flags |= win32con.LOCKFILE_FAIL_IMMEDIATELY
        hfile = win32file._get_osfhandle (file.fileno ())
        try:
            win32file.LockFileEx (hfile, flags, 0, -0x10000, __overlapped)
        except pywintypes.error as exc_value:
            # error: (33, "LockFileEx", "The process cannot access the file because another process has locked a portion of the file.")
            if exc_value [0] == 33:
                raise Lock_Failed  ()
            else:
                # Q:  Are there exceptions/codes we should be dealing with here?
                raise
    # end def _lock_impl

    def _unlock_impl (file) :
        hfile = win32file._get_osfhandle (file.fileno ())
        try:
            win32file.UnlockFileEx (hfile, 0, -0x10000, __overlapped)
        except pywintypes.error as exc_value:
            if exc_value[0] == 158:
                # error: (158, "UnlockFileEx", "The segment is already unlocked.")
                # To match the "posix" implementation, silently ignore this error
                pass
            else:
                # Q:  Are there exceptions/codes we should be dealing with here?
                raise
    # end def _unlock_impl

elif os.name == "posix":
    import fcntl
    def _lock_impl (file, exclusive, nonblocking) :
        if exclusive :
            flags = fcntl.LOCK_EX
        else :
            flags = fcntl.LOCK_SH
        if nonblocking :
            flags |= fcntl.LOCK_NB
        try:
            fcntl.flock (file.fileno (), flags)
            os.fchmod   (file.fileno (), stat.S_IRUSR | stat.S_IWUSR)
        except IOError as exc_value :
            #  Errno 11: Resource temporarily unavailable
            if exc_value.errno == 11 :
                raise Lock_Failed (file.name)
            else:
                raise
    # end def _lock_impl

    def _unlock_impl (file):
        fcntl.flock (file.fileno (), fcntl.LOCK_UN)
    # end def _unlock_impl

class Locked_File (object) :
    """Open file which optains a lock until it is closed again

       Inspired by http://code.activestate.com/recipes/65203/

    >>> with Locked_File ("test.lock", "w") as f:
    ...     _ = f.write ("Write")
    >>> with Locked_File ("test1.lock", "w") as f :
    ...     _ = f.write ("Write-Read")
    ...     with expect_except (Lock_Failed) :
    ...         with Locked_File ("test1.lock", "r", nonblocking = True) as r :
    ...             r.read ()
    Lock_Failed: test1.lock

    >>> with Locked_File ("test.lock", "r") as f :
    ...    f.read (1)
    ...    with Locked_File ("test.lock", "r", nonblocking = True) as r :
    ...        r.read (2)
    'W'
    'Wr'

    """

    def __init__ (self, file_name, mode, nonblocking = False) :
        self.file_name   = file_name
        self.mode        = mode
        self.nonblocking = nonblocking
    # end def __init__

    def __enter__ (self) :
        self._file = result = open (self.file_name, self.mode)
        self._lock ()
        return result
    # end def __enter__

    def __exit__ (self, exc_type, exc_val, exc_tb) :
        self._file.flush ()
        _unlock_impl     (self._file)
        self._file.close ()
    # end def __exit__

    def _lock (self) :
        exclusive = "w" in self.mode
        _lock_impl (self._file, exclusive, self.nonblocking)
    # end def _lock

# end class Locked_File

class File_Session (GTW.Session) :
    """Stores the session data in a file on disk.

    >>> session = File_Session ()
    >>> session.save ()
    >>> session ["name"] = "user1"
    >>> session ["lang"] = "de_AT"
    >>> session.save ()

    >>> session2 = File_Session (session.sid)
    >>> sorted (session._data.items ())
    [('lang', 'de_AT'), ('name', 'user1'), ('user', GTW.Session.User (None))]
    >>> sorted (session2._data.items ())
    [('lang', 'de_AT'), ('name', 'user1'), ('user', GTW.Session.User (None))]
    >>> session.sid == session2.sid
    True
    >>> session.name
    'user1'
    >>> session.name == session2 ["name"]
    True
    >>> session.lang == session2 ["lang"]
    True
    >>> session.get ("lang")
    'de_AT'
    >>> del session.lang
    >>> print (session.get ("lang"))
    None
    >>> session.get ("lang") == session2 ["lang"]
    False
    >>> session.remove ()
    >>> session3 = File_Session (session.sid)
    >>> session3.get ("name"), session.name
    (None, 'user1')
    >>> session3.get ("lang"), session.lang
    (None, None)
    """

    base_path       = "/tmp"
    _non_data_attrs = set (("file_name", ))

    @property
    def file_name (self) :
        return self._file_name (self.sid)
    # end def file_name

    def exists (self, sid) :
        return os.path.exists (self._file_name (sid))
    # end def exists

    def remove (self) :
        try :
            os.unlink (self.file_name)
        except EnvironmentError :
            pass
    # end def remove

    def save (self) :
        fn = self.file_name
        if bool (self) :
            with Locked_File (fn, "wb") as f :
                cPickle.dump (self._data, f)
        elif os.path.exists (fn) :
            self.remove ()
    # end def save

    def _file_name (self, sid) :
        return os.path.join (self.base_path, "%s.sid" % (sid, ))
    # end def _file_name

    def _load (self) :
        result = {}
        try :
            with Locked_File (self.file_name, "rb") as f :
                cargo = f.read ()
        except Exception as exc :
            print \
                ( ">>> Exception"
                , exc
                , "when trying to load session data from"
                , self.file_name
                , file = sys.stderr
                )
        else :
            try :
                result = cPickle.loads (cargo)
            except Exception as exc :
                print \
                    ( ">>> Exception"
                    , exc
                    , "when trying to unpickle session data from"
                    , self.file_name
                    , file = sys.stderr
                    )
        return result
    # end def _load

# end class File_Session

if __name__ != "__main__" :
    GTW._Export ("*")
### __END__ GTW.File_Session
