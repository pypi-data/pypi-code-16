# -*- coding: utf-8 -*-
# Copyright (C) 1998-2015 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Sync_File
#
# Purpose
#    File class which provides protection against loss of data by races
#    between multiple users of the file
#
# Revision Dates
#    17-Apr-1998 (CT) Creation
#     5-Mar-1999 (CT) `__str__` and `__repr__` added
#    19-Apr-1999 (CT) Remove `tmp_name` if making no backup
#    19-Apr-1999 (CT) Raise exceptions instead of returning `None`
#    12-Oct-1999 (CT) Use `sos.tempfile_name` instead of `tempfile.mktemp`
#                     and pass directory in (avoid using default directory to
#                     which the user may not have write access)
#    15-Oct-1999 (CT) `or sos.curdir` added to call of `sos.tempfile_name` to
#                     accomodate writes to current directory (for which None
#                     was passed which leads to an error because it tries to
#                     do cross device rename operations)
#    20-Jul-2000 (CT) `_get_key_save` and `_write_header` factored from `open`
#    31-Jul-2000 (CT) Attribute `exists` added
#     6-Sep-2000 (CT) `close` and locking added
#     8-Sep-2000 (CT) Support open-mode `r`, too
#     8-Sep-2000 (CT) `_open_w` factored
#     8-Sep-2000 (CT) Reraise `IOError` unless `ENOENT` in `_get_key`
#     8-Sep-2000 (CT) `Sync_DB_` factored in here
#    11-Sep-2000 (CT) Error in `open` corrected (if and else clause for
#                     `_modify_mode_pat.search` were switched)
#    11-Sep-2000 (CT) Bug in `Sync_DB_` fixed (spurious reference to `Struct`)
#    11-Sep-2000 (CT) Bug in `Sync_DB_.load` fixed (define `db`)
#    28-Sep-2000 (CT) Added missing `exc` to `except` clause in `_open_lock`
#    13-Dec-2000 (CT) s/data base/database/g
#    22-Feb-2001 (CT) Use `raise` instead of `raise exc` for re-raise
#    19-Sep-2001 (CT) `_can_lock` added to, and used in, `_open_lock`
#    21-Sep-2001 (CT) `_open_method` dictionary used instead of explicit `if`
#    21-Sep-2001 (CT) `Sync_Dir` and `Open_Sync_Dir_?` added
#    24-Sep-2001 (CT) `_get_files_from_stamp` factored
#    24-Sep-2001 (CT) `add_file` added
#     4-Oct-2001 (CT) `_Open_Sync_Dir_.openfile` changed to only add files
#                     opened for writing
#     4-Oct-2001 (CT) `path.join` moved from `add_file` to `openfile`
#    14-Dec-2001 (CT) `Could_Not_Delete_Old_DB` added and used in
#                     `Open_Sync_Dir_W.__init__` to avoid Win32 annoyances
#                     when somebody has the directory opened in Explorer
#                     while trying to save
#    27-Feb-2002 (AGO) Prepared for switching to new import mechanism
#    12-Apr-2002 (CT)  Use `StandardError` instead of `Exception`
#    12-Apr-2002 (CT)  Reraise `KeyboardInterrupt`
#    11-Jun-2003 (CT)  s/== None/is None/
#    11-Jun-2003 (CT)  s/!= None/is not None/
#    18-Aug-2003 (CT)  `_close_lock` changed to use finally clauses
#    13-May-2004 (GWA, CED) `_open_lock` changed to create multi-extension
#                           lockfiles
#     3-Jun-2004 (CT)  `traceback.print_exc` removed for `IOError` handlers
#    28-Jun-2004 (CT)  `_open_lock` changed to remove trailing `sos.sep`
#                      characters before building locknames (i.e., the lock
#                      file for a directory should be outside that directory)
#     7-Sep-2004 (CT)  Use `Filename._as_file` instead of the home-grown code
#                      introduced on 28-Jun-2004
#    15-Sep-2004 (CT)  Usages of `apply` removed
#    15-Sep-2004 (CT)  Usages of `string` module removed
#    15-Sep-2004 (CT)  `delete_file` and `_remove_file` added
#    15-Sep-2004 (CT)  `add_file` renamed to `_add_file`
#    20-Sep-2004 (CED) `delete_file` fixed to pass `name` instead of
#                      `full_name` to `_remove_file`
#    14-Feb-2006 (CT)  Moved into package `TFL`
#     1-Dec-2006 (PGO) Usage of Ordered_Set in `_remove_file` fixed
#     3-Apr-2008 (CT)  Exception classes factored into `TFL.Error`
#    ««revision-date»»···
#--

from   __future__              import print_function

from   _TFL                    import TFL
from   _TFL.Error              import *
from   _TFL.Filename           import Filename
from   _TFL                    import sos
import _TFL.d_dict
import _TFL.Environment
import _TFL.Ordered_Set

import dircache
import errno
import re
import time
import traceback

class _Sync_File_ :

    def __init__ (self, file_name, app_name, file_desc, line_start = "#") :
        self.file_name    = file_name
        self.app_name     = app_name
        self.file_desc    = file_desc
        self.line_start   = line_start
        self.changed_key  = None
        self._file        = None
        self._lock_file   = None
        self.exists       = sos.path.exists (file_name)
        if self.exists :
            self._check_type (file_name)
            self.last_key = self._get_key (self.file_name)
        else :
            self.last_key = ""
    # end def __init__

    def open (self, * args, ** kw) :
        """Check if file is unchanged and return the open'ed file object if
           so. This function creates a lock -- you *must* call `close` to
           free the lock.
        """
        result = None
        self._open_lock ()
        try :
            result = self._file = self._open (* args, ** kw)
        finally :
            if not result :
                self._close_lock ()
        return result
    # end def open

    def close (self) :
        "Close the file and free the lock."
        self._close      ()
        self._close_lock ()
    # end def close

    def _close (self) :
        if self._file :
            self._file.close ()
        else :
            raise Not_Open (self.file_name)
    # end def _close

    def _close_lock (self) :
        if self._lock_file :
            try :
                try :
                    sos.close  (self._lock_file)
                finally :
                    sos.remove (self._lfile_name)
            finally :
                self._lock_file = self._lfile_name = None
    # end def _close_lock

    def _get_key (self, file_name) :
        result = ""
        try :
            f  = self._open_key_file (file_name, "r")
            try :
                result = f.readline ()
            finally :
                f.close ()
        except (SystemExit, KeyboardInterrupt) as exc :
            raise
        except IOError as exc :
            if exc.args [0] != errno.ENOENT :
                raise
        except :
            pass
        return result
    # end def _get_key

    def _open (self, mode = "wb", bufsize = -1, backup_name = ".bak") :
        opener = getattr (self, self._open_method [mode [0]])
        return opener (mode, bufsize, backup_name)
    # end def _open

    def _open_lock (self) :
        if self._lock_file :
            raise Already_Open
        try :
            fn    = Filename._as_file (self.file_name)
            fname = Filename (fn + ".lock", absolute = 1)
            self._can_lock = sos.access (fname.directory, sos.W_OK)
            if self._can_lock :
                self._lfile_name = name = fname.name
                self._lock_file  = sos.open (name, sos.O_CREAT | sos.O_EXCL)
        except sos.error as exc :
            if exc.args [0] != errno.EEXIST :
                raise
            raise Sync_Conflict (self.file_name)
    # end def _open_lock

    def _write_header (self, file) :
        user = _TFL.Environment.username
        host = _TFL.Environment.hostname
        if user : user = " by user " + user
        if host : host = " on host " + host
        new_key = \
            ( "%s %s %s, written on %s%s%s\n"
            % ( self.line_start
              , self.app_name
              , self.file_desc
              , time.strftime
                  ("%a %d-%b-%Y %H:%M:%S", time.localtime (time.time ()))
              , user
              , host
              )
            )
        file.write (new_key)
        self.last_key = new_key
    # end def _write_header

    def __str__ (self) :
        return "%s (%s of %s, last-key: %s)" % \
            (self.file_name, self.file_desc, self.app_name, self.last_key)
    # end def __str__

    def __repr__ (self) :
        return "%s (%s, %s, %s, %s)" % \
            ( self.__class__.__name__
            , self.file_name
            , self.app_name
            , self.file_desc
            , self.line_start
            )
    # end def __repr__

# end class _Sync_File_

class Sync_File (_Sync_File_) :

    Ancestor = __Ancestor = _Sync_File_

    _open_method          = TFL.d_dict \
      ( a                 = "_open_w"
      , r                 = "_open_r"
      , w                 = "_open_w"
      )

    def _check_type (self, file_name) :
        if not sos.path.isfile (file_name) :
            print \
                ( file_name
                , sos.path.exists (file_name)
                , sos.path.isfile (file_name)
                )
            raise Not_A_File (file_name)
    # end def _check_type

    def _open_r (self, mode, bufsize, backup_name) :
        return open (self.file_name, mode, bufsize)
    # end def _open_r

    def _open_w (self, mode, bufsize, backup_name) :
        """Open locked file for writing"""
        curr_key, tmp_name = self._get_key_save ()
        result = None
        try :
            if curr_key == self.last_key :
                if curr_key :
                    if backup_name :
                        bak_name = Filename (backup_name, self.file_name).name
                        self.backup_name = bak_name
                        sos.rename (tmp_name, bak_name)
                    else :
                        self.backup_name = None
                        sos.remove (tmp_name)
                result      = open (self.file_name, mode, bufsize)
                self.exists = 1
            else :
                self.changed_key = curr_key
                raise Sync_Conflict (self)
        finally :
            if not result :
                sos.rename         (tmp_name, self.file_name)
            else :
                self._write_header (result)
        return result
    # end def _open_w

    def _open_key_file (self, file_name, mode) :
        return open (file_name, mode, 1)
    # end def _open_key_file

    def _get_key_save (self) :
        ### get current key of file
        ###     to make it save, rename the file first and read key afterwards
        tmp_name = sos.tempfile_name \
            (Filename (self.file_name).directory or sos.curdir)
        curr_key = ""
        try :
            sos.rename (self.file_name, tmp_name)
            curr_key = self._get_key (tmp_name)
        except sos.error as exc :
            if exc.args [0] != errno.ENOENT :
                raise
            tmp_name = None
        except (SystemExit, KeyboardInterrupt, IOError) as exc :
            raise
        except :
            pass
        return curr_key, tmp_name
    # end def _get_key_save

# end class Sync_File

class _Open_Sync_Dir_ :

    def __init__ (self, sync_dir, mode, default_mode, bufsize, backup_name) :
        self.sync_dir        = sync_dir
        self.name            = sync_dir.file_name
        self.stamp           = None
        self.default_mode    = default_mode + mode [1:]
        self.bufsize         = bufsize
        self.last_file       = None
        self.files           = TFL.Ordered_Set ()
        if backup_name :
            self.backup_name = Filename \
                (backup_name, self.sync_dir.file_name).name
        else :
            self.backup_name = None
    # end def __init__

    def close (self) :
        self.closefile          ()
        self._close_stamp_file  ()
        if self.sync_dir._file  :
            ### if `self.close` was called by `self.sync_dir`,
            ### `self.sync_dir._file` will be None. Otherwise, call
            ### `self.sync_dir.close` here
            self.sync_dir.close ()
    # end def close

    def closefile (self, file = None) :
        file = file or self.last_file
        if file :
            file.close ()
        self.last_file = None
    # end def closefile

    def delete_file (self, name) :
        full_name = sos.path.join (self.name, name)
        if self.last_file and self.last_file.name == full_name :
            self.closefile ()
        self._remove_file  (name)
        sos.unlink         (full_name)
    # end def delete_file

    def openfile (self, name, mode = None, bufsize = None, * args, ** kw) :
        self.closefile ()
        full_name      = sos.path.join (self.name, name)
        mode           = mode or self.default_mode
        bufsize        = [bufsize, self.bufsize] [bufsize is None]
        self.last_file = open (full_name, mode, bufsize, * args, ** kw)
        if not mode.startswith ("r") :
            self._add_file (name)
        return self.last_file
    # end def openfile

    def _add_file (self, name) :
        if name not in self.files :
            self.files.append (name)
    # end def _add_file

    def _check_exists (self) :
        name = self.sync_dir.file_name
        if not sos.path.isdir (name) :
            raise Not_A_Dir (name)
        self._get_files_from_stamp ()
    # end def _check_exists

    def _close_stamp_file (self) :
        if self.stamp :
            for f in self.files :
                self.stamp.write (f)
                self.stamp.write ("\n")
            self.stamp.close ()
            self.stamp = None
    # end def _close_stamp_file

    def _get_files_from_stamp (self) :
        self._open_stamp_file ()
        self.files = TFL.Ordered_Set \
            ( filter ( None
                     , [ f.strip () for f in self.stamp.readlines ()
                         if self.not_comment_line (f)
                       ]
                     )
            )
        self.stamp.close ()
        self.stamp = None
    # end def _get_files_from_stamp

    def _open_stamp_file (self, dir_name = None, mode = "rb") :
        sync_dir   = self.sync_dir
        name       = dir_name or sync_dir.file_name
        self.stamp = sync_dir._open_key_file (name, mode)
        return self.stamp
    # end def _open_stamp_file

    def _remove_file (self, name) :
        if name in self.files :
            self.files.remove (name)
    # end def _remove_file

    def _write_stamp_file_header (self, dir_name = None) :
        self._open_stamp_file       (dir_name, mode = "wb")
        self.sync_dir._write_header (self.stamp)
    # end def _write_stamp_file

    def not_comment_line (self, line) :
        return not line.startswith (self.sync_dir.line_start)
    # end def not_comment_line

# end class _Open_Sync_Dir_

class Open_Sync_Dir_M (_Open_Sync_Dir_) :

    Ancestor = __Ancestor = _Open_Sync_Dir_

    def __init__ (self, sync_dir, mode, bufsize, bak_name) :
        self.__Ancestor.__init__ (self, sync_dir, mode, "w", bufsize, bak_name)
        self._check_exists       ()
        self._write_stamp_file_header ()
    # end def __init__

# end class Open_Sync_Dir_M

class Open_Sync_Dir_R (_Open_Sync_Dir_) :

    Ancestor = __Ancestor = _Open_Sync_Dir_

    def __init__ (self, sync_dir, mode, bufsize, bak_name) :
        self.__Ancestor.__init__ (self, sync_dir, mode, "r", bufsize, bak_name)
        self._check_exists       ()
    # end def __init__

    def __getitem__ (self, key) :
        return self.openfile (self.files [key])
    # end def __getitem__

# end class Open_Sync_Dir_R

class Open_Sync_Dir_W (_Open_Sync_Dir_) :

    Ancestor = __Ancestor = _Open_Sync_Dir_

    def __init__ (self, sync_dir, mode, bufsize, bak_name) :
        self.__Ancestor.__init__ (self, sync_dir, mode, "w", bufsize, bak_name)
        name = self.sync_dir.file_name
        if sos.path.exists (name) :
            if bak_name :
                name = sos.tempfile_name \
                    (Filename (name).directory or sos.curdir)
                sos.mkdir (name)
            else :
                sos.rmdir (name, deletefiles = 1)
                if sos.path.exists (name) :
                    raise Could_Not_Delete_Old_DB \
                        ( "Deleting %s failed without error message from "
                          "the OS. Try saving to a different database."
                        % (name, )
                        )
                try :
                    sos.mkdir (name)
                except (IOError, OSError) :
                    raise Could_Not_Delete_Old_DB \
                        ( "Deleting %s failed without error message from "
                          "the OS. Try saving to a different database."
                        % (name, )
                        )
        else :
            sos.mkdir (name)
        self.name = name
        self._write_stamp_file_header (name)
    # end def __init__

    def close (self) :
        if self.name != self.sync_dir.file_name :
            assert self.backup_name
            if sos.path.isdir (self.backup_name) :
                sos.rmdir (self.backup_name, deletefiles = 1)
            sos.rename (self.sync_dir.file_name, self.backup_name)
            sos.rename (self.name,               self.sync_dir.file_name)
            self.name = self.sync_dir.file_name
        self.__Ancestor.close (self)
    # end def close

# end class Open_Sync_Dir_W

class Sync_Dir (_Sync_File_) :

    Ancestor = __Ancestor = _Sync_File_
    stamp_name            = ".stamp"

    _open_method          = TFL.d_dict \
      ( M                 = "_open_m"
      , r                 = "_open_r"
      , w                 = "_open_w"
      )

    def _check_type (self, file_name) :
        if not sos.path.isdir (file_name) :
            raise Not_A_Dir (file_name)
    # end def _check_type

    def _close (self) :
        if self._file :
            ### setting `_file` to None before calling its `close` allows the
            ### user to call either `self.close` or `self._file.close`
            sync_file  = self._file
            self._file = None
            sync_file.close ()
        else :
            raise Not_Open (self.file_name)
    # end def _close

    def _open_key_file (self, file_name, mode) :
        name = sos.path.join (file_name, self.stamp_name)
        return open (name, mode, 1)
    # end def _open_key_file

    def _open_m (self, mode, bufsize, backup_name) :
        return Open_Sync_Dir_M (self, mode, bufsize, backup_name)
    # end def _open_r

    def _open_r (self, mode, bufsize, backup_name) :
        return Open_Sync_Dir_R (self, mode, bufsize, backup_name)
    # end def _open_r

    def _open_w (self, mode, bufsize, backup_name) :
        return Open_Sync_Dir_W (self, mode, bufsize, backup_name)
    # end def _open_w

# end class Sync_Dir

class Sync_DB_ :
    """Root class for simple synchronized databases"""

    def __init__ (self, comment_start = "#", file_name = None) :
        self.comment_pat = re.compile ( r"\s*%s" % comment_start)
        self.data_base   = None
        if file_name :
            self.load (file_name)
    # end def __init__

    def load (self, file_name) :
        """Load user data from file named `file_name`"""
        assert (file_name)
        assert (self.data_base is None)
        db = self.data_base = self._sync_file (file_name)
        if not self.data_base.last_key :
            print ("No key in db file %s" % file_name)
        else :
            try :
                file = db.open ("r")
            except Already_Open as exc :
                ### traceback.print_exc ()
                print \
                    ( "The %s `%s` is currently locked by another user"
                    % (db.file_desc, db.file_name)
                    )
                raise Already_Open (db)
            except KeyboardInterrupt :
                raise
            except Exception as exc :
                ### traceback.print_exc ()
                print \
                    ( "The %s `%s` couldn't be opened for reading due "
                      "to exception\n    `%s`"
                    % (db.file_desc, db.file_name, str (exc))
                    )
                raise
            try :
                self._load_add (file)
            finally :
                db.close       ()
    # end def load

    def load_add (self, file_name) :
        """Add user data from file named `file_name` to db"""
        assert (file_name)
        assert (self.data_base is not None)
        file = open (file_name, "r")
        try :
            self._load_add (file)
        finally :
            file.close     ()
    # end def load_add

    def save (self) :
        """Save user data to file"""
        assert (self.data_base is not None)
        db = self.data_base
        try :
            file = db.open ()
        except Sync_Conflict as exc :
            ### traceback.print_exc ()
            print \
                ( "The %s `%s` was changed since you started to work on it"
                % (db.file_desc, db.file_name)
                )
            raise Sync_Error (db)
        except KeyboardInterrupt :
            raise
        except Exception as exc :
            ### traceback.print_exc ()
            print \
                ( "The %s `%s` couldn't be opened for writing "
                  "due to exception\n    `%s`"
                % (db.file_desc, db.file_name, str (exc))
                )
            raise
        try :
            self._save_data (file)
        finally :
            db.close ()
    # end def save

# end class Sync_DB_

if __name__ != "__main__" :
    TFL._Export ("*", "_Sync_File_", "_Open_Sync_Dir_")
### __END__ TFL.Sync_File
