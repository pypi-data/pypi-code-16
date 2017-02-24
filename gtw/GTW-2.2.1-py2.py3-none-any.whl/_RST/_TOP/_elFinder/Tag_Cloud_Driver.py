# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Martin Glueck All rights reserved
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
#    GTW.RST.TOP.elFinder.Tag_Cloud_Driver
#
# Purpose
#    file system driver for the tag cloud for the jquery file browser
#    `elfinder 2`
#    http://elfinder.org/
#
# Revision Dates
#    29-Jan-2013 (MG) Creation
#    30-Jan-2013 (MG) Move `add` from `_Filesystem_Driver_`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW                       import GTW
from   _MOM                       import MOM
from   _TFL                       import TFL

from   _GTW._RST._TOP._elFinder   import elFinder

from   _MOM.import_MOM            import Q

from   _TFL                       import sos as os
from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL.pyk                   import pyk

import _GTW._RST._TOP.Page
import _GTW._RST._TOP._elFinder._Filesystem_Driver_

import datetime
import mimetypes
import time
import PIL.Image

class Tag_Cloud_Driver (elFinder._Filesystem_Driver_) :
    """Creates on directory for each tag."""

    def __init__ (self, root_dir, ETM, name, ** kw) :
        self.thumb_directory = kw.pop ("thumb_directory", None)
        self.__super.__init__ (name, ** kw)
        self._ETM     = ETM
        self.root_dir = root_dir
    # end def __init__

    def abs_path (self, obj) :
        return obj.abs_path
    # end def abs_path

    def add (self, path_spec, upload) :
        import werkzeug ### XXX
        path, dir, file = path_spec
        if file :
            raise elFinder.Error ("errTrgFolderNotFound")
        abs_file_name = os.path.join \
            ( self.root_dir, dir.name
            , werkzeug.secure_filename (upload.filename)
            )
        rel_file_name  = abs_file_name.replace (MOM.Web_Src_Root, "")
        upload.save                            (abs_file_name)
        i    = PIL.Image.open                  (abs_file_name)
        w, h = i.size
        file = self.ETM        (path = rel_file_name, width = w, height = h)
        self._scope.MOM.Id_Entity_has_Tag (file, ddir)
        return self.file_entry            (dir, file)
    # end def add

    def copy (self, src_path_spec, dst_volume, dst_path_spec, remove = False) :
        spath, sdir, sfile = src_path_spec
        dpath, ddir, dfile = dst_path_spec
        if not sfile :
            raise _Error_ ("errNotFile")
        if not ddir :
            raise _Error_ ("errNotFolder")
        if dfile :
            raise _Error_ ("errCmdParams")
        dfile  = dst_volume._copy_from (ddir, self, sdir, sfile)
        result = dict (added = [dst_volume.file_entry (ddir, dfile)])
        if remove :
            result ["removed"] = [self.file_entry (sdir, sfile) ["hash"]]
            self.remove (src_path_spec)
        return result
    # end def copy

    def _copy_from (self, ddir, svolume, sdir, sfile, buf_size = 16 * 1024) :
        if svolume is not self :
            shandle   = svolume._open_file   (sdir,      sfile)
            dhandle   = self   ._create_file (ddir.name, sfile.name)
            while True :
                buffer = shandle.read (buf_size)
                if buffer :
                    dhandle.write     (buf_size)
                else :
                    break
            shandle.close        ()
            dhandle.close        ()
            return self.add_file (ddir, sfile.name)
        self._scope.MOM.Id_Entity_has_Tag (sfile, ddir)
        return sfile
    # end def _copy_from

    def _create_file (self, dir, file) :
        if isinstance (file, pyk.string_types) :
            file_name = os.path.join (self.root_dir, dir, file)
        return open (file_name, "wb")
    # end def _create_file

    def current_directory_options (self, path) :
        path, dir, file = path
        disabled        = ["mkfile", "extract", "archive", "duplicate"]
        if dir :
            disabled.append ("mkdir")
        else :
            disabled.append ("upload")
        return dict (disabled = disabled)
    # end def current_directory_options

    def decode_hashes (self, hashes) :
        if len (hashes) > 2 :
            raise _Error_ ("errCmdParams")
        result = []
        dir    = None
        file   = None
        if hashes :
            dir_name = hashes.pop (0)
            dir      = self.TETM.pid_query (dir_name)
            if not dir :
                raise _Error_ ("errFolderNotFound", dir_name)
            result.append            (dir.name)
        if hashes :
            file_name = hashes.pop         (0)
            file      = self.ETM.pid_query (file_name)
            if not file :
                raise _Error_ ("errFileNotFound", file_name)
            result.append            (file.name)
        return "/".join (result), dir, file
    # end def decode_hashes

    def directories (self, dir) :
        if dir : ### tag of tag no supported
            return []
        return self.TETM.query ()
    # end def directories

    def directory_entry (self, tag) :
        return dict \
            ( mime      = "directory"
            , ts        = time.mktime (self.started.timetuple ())
            , read      = self.allow_read
            , write     = self.allow_write
            , size      = 0
            , hash      = "%s_%s" % (self.hash, tag.pid)
            , phash     = self.hash
            , name      = tag.name
            , date      = self.started.strftime ("%c")
            , dirs      = 0
            )
    # end def directory_entry

    def dirs_of_path (self, path, dir) :
        return (None, dir)
    # end def dirs_of_path

    @Once_Property
    def ETM (self) :
        return self._scope [self._ETM]
    # end def ETM

    def files_in_directory (self, tag) :
        if tag :
            return self.ETM.query (Q.tags.CONTAINS (tag))
        return ()
    # end def files_in_directory

    def file_entry (self, tag, obj) :
        path      = self.abs_path   (obj)
        mime_type = self.mime_type  (obj)
        stat      = os.stat         (path)
        result    = dict \
            ( mime      = mime_type
            , ts        = stat.st_mtime
            , hash      = "%s_%s_%s" % (self.hash, tag.pid, obj.pid)
            , phash     = "%s_%s"    % (self.hash, tag.pid)
            , read      = self.allow_read
            , write     = self.allow_write
            , size      = stat.st_size
            , name      = obj.name
            , date      = datetime.datetime.fromtimestamp
                (stat.st_mtime).strftime ("%c")
            , dim       = "%dx%d" % (obj.width, obj.height)
            )
        if self.media_domain :
            result ["url"] = "%s/%s" % (self.media_domain, obj.path)
            if self.thumb_directory :
                result ["tmb"] = "%s/%s" % (self.media_domain, obj.thumb_path)
        return result
    # end def file_entry

    def file_name (self, dir, file) :
        return file.name
    # end def file_name

    @property
    def has_directories (self) :
        return self.TETM.count > 0
    # end def has_directories

    def image_dimensions (self, path, dir, file) :
        return "%dx%d" % (file.width, file.height)
    # end def image_dimensions

    def mime_type (self, obj) :
        result = obj.mime_type
        if result is None :
            result = obj.mime_type = mimetypes.guess_type (obj.abs_path) [0]
        return result
    # end def mime_type

    def mkdir (self, dir, name) :
        ### a directory for in the tag cloud is ceating a new tag
        dir_name = os.path.join     (self.root_dir, name)
        if not os.path.isdir        (dir_name) :
            os.makedirs             (dir_name)
        tag      = self.TETM        (name)
        return self.directory_entry (tag)
    # end def mkdir

    def _open_file (self, dir, file) :
        return open (file.abs_path, "rb")
    # end def _open_file

    def remove (self, path_spec) :
        path, dir, file = path_spec
        EhT             = self._scope.MOM.Id_Entity_has_Tag
        if file :
            entry = self.file_entry (dir, file)
            EhT.query               (right = dir, left = file).one ().destroy ()
            if not file.tags :
                file.destroy        ()
        else :
            if not EhT.query (Q.tag == dir).count () :
                entry = self.directory_entry (dir)
                dir.destroy                  ()
            else :
                raise _Error_ ("errUsupportType")
        return entry
    # end def remove

    def rename (self, new_name, dir, file) :
        if file :
            ### rename the file
            file_name = self.abs_path (file)
            root_dir  = file_name [:-len (file.path)]
            new_name  = os.path.join (os.path.dirname (file_name), new_name)
            os.rename    (file_name, new_name)
            file.set_raw (path = new_name [len (root_dir):])
            return self.file_entry (dir, file)
        else :
            ### rename the tag
            dir.set_raw (name = new_name)
            return self.directory_entry (dir)
    # end def rename

    @Once_Property
    def TETM (self) :
        return self._scope.MOM.Tag
    # end def TETM

# end class Tag_Cloud_Driver

if __name__ != "__main__" :
    GTW.RST.TOP.elFinder._Export ("*")
### __END__ GTW.RST.TOP.elFinder.Tag_Cloud_Driver
