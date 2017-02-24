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
#    GTW.RST.TOP.elFinder.Gallery_Driver
#
# Purpose
#    File system driver for galleries for the jquery file browser
#    `elfinder 2`
#    http://elfinder.org/
#
# Revision Dates
#    29-Jan-2013 (MG) Creation
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

class Gallery_Driver_elFinder (elFinder._Filesystem_Driver_) :
    """Creates a directory for each gallery."""

    _real_name = "Gallery_Driver"

    def __init__ ( self, name, root_dir, filter = None
                 , gallery_e_type = "SWP.Gallery"
                 , picture_e_type = "SWP.Picture"
                 , thum_size      = (96, 96)
                 ) :
        self.__super.__init__ (name, ** kw)
        self.root_dir         = root_dir
        self.filter           = filter
        self._GETM            = gallery_e_type
        self._PETM            = picture_e_type
        self.thum_size        = thum_size
    # end def __init__

    def abs_path (self, obj) :
        return obj.photo.path
    # end def abs_path

    def add (self, path_spec, upload) :
        import werkzeug ### XXX
        path, gallery, file = path_spec
        MOM                 = self._scope.MOM
        if file :
            raise elFinder.Error ("errTrgFolderNotFound")
        pics = sorted (gallery.pictures, key = lambda p : -p.number)
        if pics :
            number = pics [0].number + 1
        else :
            number = 0
        name, ext = os.path.splitext \
            (werkzeug.secure_filename (upload.filename))
        img  = self.PETM \
            ( gallery
            , number = number
            , name   = name
            , photo  = MOM._Pic_
                ( extension = ext
                )
            , thumb  = MOM._Thumb_
                ( extension = ext
                )
            )
        upload.save                                        (img.photo.path)
        i                                 = PIL.Image.open (img.photo.path)
        img.photo.width, img.photo.height = i.size
        i.thumbnail (self.thum_size, PIL.Image.ANTIALIAS)
        i.save      (img.thumb.path)
        img.thumb.width, img.thumb.height = i.size
        return self.file_entry (gallery, img)
    # end def add

    def copy (self, src_path_spec, dst_volume, dst_path_spec, remove = False) :
        spath, sdir, sfile = src_path_spec
        dpath, ddir, dfile = dst_path_spec
        if not sfile :
            raise elFinder.Error ("errNotFile")
        if not ddir :
            raise elFinder.Error ("errNotFolder")
        if dfile :
            raise elFinder.Error ("errCmdParams")
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
            raise elFinder.Error ("errCmdParams")
        result = []
        dir    = None
        file   = None
        if hashes :
            dir_name = hashes.pop          (0)
            dir      = self.GETM.pid_query (dir_name)
            if not dir :
                raise elFinder.Error        ("errFolderNotFound", dir_name)
            result.append                   (dir.perma_name)
        if hashes :
            file_name = hashes.pop          (0)
            file      = self.PETM.pid_query (file_name)
            if not file :
                raise elFinder.Error        ("errFileNotFound", file_name)
            result.append                   (file.name)
        return "/".join (result), dir, file
    # end def decode_hashes

    def directories (self, dir) :
        if dir : ### gallery in gallery not supported
            return ()
        result = self.GETM.query ()
        if self.filter is not None :
            result.filter (self.filter)
        return result
    # end def directories

    def directory_entry (self, gallery) :
        return dict \
            ( mime      = "directory"
            , ts        = time.mktime (self.started.timetuple ())
            , read      = self.allow_read
            , write     = self.allow_write
            , size      = 0
            , hash      = "%s_%s" % (self.hash, gallery.pid)
            , phash     = self.hash
            , name      = gallery.title or gallery.perma_name
            , date      = self.started.strftime ("%c")
            , dirs      = 0
            )
    # end def directory_entry

    def dirs_of_path (self, path, dir) :
        return (None, dir)
    # end def dirs_of_path

    @Once_Property
    def GETM (self) :
        return self._scope [self._GETM]
    # end def GETM

    @Once_Property
    def PETM (self) :
        return self._scope [self._PETM]
    # end def PETM

    def files_in_directory (self, gallery) :
        if gallery :
            return gallery.pictures
        return ()
    # end def files_in_directory

    def file_entry (self, gallery, obj) :
        path      = self.abs_path   (obj)
        mime_type = self.mime_type  (obj, path)
        stat      = os.stat         (path)
        result    = dict \
            ( mime      = mime_type
            , ts        = stat.st_mtime
            , hash      = "%s_%s_%s" % (self.hash, gallery.pid, obj.pid)
            , phash     = "%s_%s"    % (self.hash, gallery.pid)
            , read      = self.allow_read
            , write     = self.allow_write
            , size      = stat.st_size
            , name      = obj.name
            , date      = datetime.datetime.fromtimestamp
                (stat.st_mtime).strftime ("%c")
            , dim       = "%dx%d" % (obj.photo.width, obj.photo.height)
            )
        if self.media_domain :
            result ["url"] = "%s/%s" % (self.media_domain, obj.photo.path)
            result ["tmb"] = "%s/%s" % (self.media_domain, obj.thumb.path)
        return result
    # end def file_entry

    def file_name (self, dir, file) :
        return file.name
    # end def file_name

    @property
    def has_directories (self) :
        result = self.GETM.query ()
        if self.filter is not None :
            result.filter (self.filter)
        return result.count () > 0
    # end def has_directories

    def image_dimensions (self, path, dir, file) :
        return "%dx%d" % (file.photo.width, file.photo.height)
    # end def image_dimensions

    def mime_type (self, obj, abs_path) :
        result = getattr (obj, "mime_type", None)
        if result is None :
            result = obj.mime_type = mimetypes.guess_type (abs_path) [0]
        return result
    # end def mime_type

    def mkdir (self, dir, name) :
        dir_name = os.path.join     (self.root_dir, name)
        if not os.path.isdir        (dir_name) :
            os.makedirs             (dir_name)
            for d in "th", "im" :
                os.mkdir (os.path.join (dir_name, d))
        gallery      = self.GETM    (name, directory = dir_name)
        self._mkdir                 (gallery)
        return self.directory_entry (gallery)
    # end def mkdir

    def _mkdir (self, gallery) :
        pass
    # end def _mkdir

    def _open_file (self, dir, file) :
        return open (file.path, "rb")
    # end def _open_file

    def remove (self, path_spec) : ### XXX
        path, gallery, picture = path_spec
        if picture:
            entry = self.file_entry (gallery, picture)
            picture.destroy         ()
        else :
            if not gallery.pictures :
                entry = self.directory_entry (gallery)
                gallery.destroy               ()
            else :
                raise elFinder.Error ("errUsupportType")
        return entry
    # end def remove

    def rename (self, new_name, dir, file) : ### XXX
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

Gallery_Driver = Gallery_Driver_elFinder # end class

if __name__ != "__main__" :
    GTW.RST.TOP.elFinder._Export ("*")
### __END__ GTW.RST.TOP.elFinder.Gallery_Driver
