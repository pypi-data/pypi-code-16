# -*- coding: utf-8 -*-
# Copyright (C) 2013 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.TOP.elFinder.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.TOP.elFinder._Filesystem_Driver_
#
# Purpose
#    File system driver for the jquery file browser `elfinder 2`
#    http://elfinder.org/
#
# Revision Dates
#    29-Jan-2013 (MG) Creation
#    30-Jan-2013 (MG) Move `add` into `Tag_Cloud_Driver`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from    _GTW                       import GTW
import  _GTW._RST._TOP._elFinder.Error
from    _MOM                       import MOM
from    _TFL                       import TFL
from    _TFL                       import sos as os
from    _TFL._Meta.Once_Property   import Once_Property
import   PIL.Image
import   time
import   datetime
from    _GTW._RST._TOP._elFinder   import elFinder
import  _GTW._RST._TOP._elFinder.Error

class _Filesystem_Driver_ (TFL.Meta.Object) :
    """Base class for the file system driver"""

    def __init__ ( self, name
                 , default      = False
                 , alias        = None
                 , allow_read   = True
                 , allow_write  = True
                 , locked       = True
                 , media_domain = None
                 ) :
        self.name         = name
        self.default      = default
        self.allow_read   = allow_read
        self.allow_write  = allow_write
        self.locked       = locked
        self.alias        = alias
        self.media_domain = media_domain
    # end def __init__

    def initialize (self, scope, hash) :
        self._scope    = scope
        self.volume_id = hash
        self.hash      = "%sR" % (hash, )
        self.started   = datetime.datetime.now ()
    # end def initialize

    def current_directory (self, path) :
        path, dir, file = path
        if not path : ### return the volume description
            return self.volume_entry ()
        return self.directory_entry  (dir)
    # end def current_directory

    def current_directory_options (self, path) :
        return {}
    # end def current_directory_options

    def files (self, path, tree) :
        path, dir, file = path
        files          = []
        options        = dict ()
        if not dir :
            files.append (self.volume_entry ())
        for d in self.directories (dir) :
            files.append (self.directory_entry (d))
        for f in self.files_in_directory (dir) :
            files.append (self.file_entry (dir, f))
        if tree and dir :
            files.extend (self.tree ((path, dir, file)))
        return files, options
    # end def files

    def mkdir (self, dir, name) :
        raise elFinder.Error ("mkdir", name)
    # end def mkdir

    def tree (self, path) :
        path, dir, file = path
        result          = []
        if not dir :
            raise elFinder.Error ("errCmdParams")
        else :
            result.append (self.volume_entry ())
            for b in self.dirs_of_path (path, dir) :
                for d in self.directories (b) :
                    result.append (self.directory_entry (d))
        return result
    # end def tree

    def volume_entry (self) :
        result = dict \
            ( mime        = "directory"
            , ts          = time.mktime (self.started.timetuple ())
            , read        = self.allow_read
            , write       = self.allow_write
            , locked      = self.locked
            , size        = 0
            , name        = self.name
            , volumeid    = self.volume_id
            , hash        = self.hash
            , date        = self.started.strftime ("%c")
            , dirs        = 1 if self.has_directories else 0
            )
        if self.alias :
            result ["alias"] = self.alias
        return result
    # end def volume_entry

# end class _Filesystem_Driver_

if __name__ != "__main__" :
    GTW.RST.TOP.elFinder._Export ("_Filesystem_Driver_")
### __END__ GTW.RST.TOP.elFinder._Filesystem_Driver_
