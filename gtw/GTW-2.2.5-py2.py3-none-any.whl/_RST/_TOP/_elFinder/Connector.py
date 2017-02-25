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
#    GTW.RST.TOP.elFinder.Connector
#
# Purpose
#    Backend for the jquery file browser `elfinder 2`
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

from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL.pyk                   import pyk
from   _TFL                       import sos as os

import _GTW._RST._TOP.Page

from   _GTW._RST._TOP._elFinder   import elFinder
import _GTW._RST._TOP._elFinder.Error

import mimetypes
import PIL.Image

class _Download_ (GTW.RST.Mime_Type._Base_) :
    """Renderer which forces the browser to open the download dialog"""

    block_size = 50 * 1024

    def __init__ (self, method, resource, path) :
        self.mime_types = (mimetypes.guess_type (path) [0], )
        self.__super.__init__ (method, resource)
    # end def __init__

    def rendered (self, request, response, body) :
        path            = body.pop ("path")
        with open (path, "rb") as file :
            data = True
            while data :
                data = file.read (self.block_size)
                if data :
                    response.write (data)
                else :
                    break
    # end def rendered

# end class _Download_

_Ancestor = GTW.RST.TOP.Page

class Window (_Ancestor) :
    """Display the elFinder window."""

    page_template_name = "html/elfinder.jnj"

# end class Window

class Connector (_Ancestor) :
    """Backend for the jQuery file browser efFinder 2"""

    def __init__ (self, * args, ** kw) :
        roots                   = kw.pop ("roots")
        self.__super.__init__ (* args, ** kw)
        self.roots              = {}
        self.mount_errors       = []
        default                 = None
        for i, r in enumerate (roots) :
            try :
                r.initialize (self.scope, "r%02d" % (i, ))
            except Exception as e :
                self.mount_errors.append (pyk.text_type (e))
            else :
                if r.default :
                    default         = r
                self.roots [r.hash] = r
        if not default :
            default             = roots [0]
        self.default_root       = default
    # end def __init__

    def strip_volume (self, target) :
        volume     = self.default_root
        hashes     = ()
        if target :
            hashes = target.split ("_")
            try :
                volume = self.roots [hashes.pop (0)]
            except KeyError :
                pass
        return volume, volume.decode_hashes (hashes)
    # end def strip_volume

    class Connector_POST (GTW.RST.POST) :

        _renderers = (GTW.RST.Mime_Type.JSON, )
        _real_name = "POST"

        def _response_body (self, resource, request, response) :
            req_data          = request.req_data
            result            = dict ()
            tree              = int (req_data.get ("tree", "0"))
            init              = int (req_data.get ("init", "0"))
            volume, path_spec = resource.strip_volume (req_data ["target"])
            added             = []
            for file in pyk.itervalues (request.req_data.files) :
                added.append (volume.add (path_spec, file))
            return dict (added = added)
        # end def _response_body

    POST = Connector_POST # end class

    class Connector_GET (_Ancestor.GET) :
        """Base class for all get requestes"""

        _real_name      = "GET"
        _renderers      = (GTW.RST.Mime_Type.JSON, )

        def _response_body (self, resource, request, response) :
            req_data          = request.req_data
            volume, path_spec = resource.strip_volume (req_data.get ("target"))
            try :
                cmd           = req_data.get ("cmd", None)
                handler       = getattr \
                    (resource, "_handle_%s" % (cmd, ), None)
                if handler is not None :
                    result    = handler \
                        (request, response, self, volume, path_spec)
                else :
                    result    = dict \
                        ( error = [ "errUnknownCmd" if cmd is None else
                                    "errCmdNoSupport"
                                  , cmd or ""
                                  ]
                        )
            except elFinder.Error as error :
                return dict (error = error.json_cargo)
            return result
        # end def _response_body

    GET = Connector_GET # end class

    def _is_file (self, volume, file) :
        if not file :
            raise elFinder.Error ("errCmdParams")
    # end def _is_file

    def _is_image (self, volume, file) :
        self._is_file            (volume, file)
        mime = volume.mime_type  (file)
        if not mime.startswith   ("image") :
            raise elFinder.Error ("errUsupportType")
    # end def _is_image

    def _handle_open (self, request, response, method, volume, path_spec) :
        req_data             = request.req_data
        result               = dict ()
        tree                 = int (req_data.get ("tree", "0"))
        init                 = int (req_data.get ("init", "0"))
        result ["cwd"]       = volume.current_directory  (path_spec)
        files, options       = volume.files              (path_spec, tree)
        options.update (volume.current_directory_options (path_spec))
        result ["files"]     = files
        result ["options"]   = options
        if  init :
            result ["api"]        = "2.0"
            result ["uplMaxSize"] = "2M"
            result ["netDrivers"] = []
            if path_spec [0] :
               result ["files"].insert (0, volume.volume_entry ())
        return result
    # end def _handle_open

    def _handle_parents (self, request, response, method, volume, path_spec) :
        return dict (tree = volume.tree  (path_spec))
    # end def _handle_parents

    def _handle_tree (self, request, response, method, volume, path_spec) :
       return dict (tree = volume.tree  (path_spec))
    # end def _handle_tree

    def _handle_dim (self, request, response, method, volume, path_spec) :
        path, dir, file      = path_spec
        self._is_image (file)
        return dict (dim = volume.image_dimensions (path, dir, file))
    # end def _handle_dim

    def _handle_file (self, request, response, method, volume, path_spec) :
        path, dir, file      = path_spec
        self._is_file (volume, file)
        file_path            = volume.abs_path (file)
        print (file.path)
        response.renderer    = _Download_ (method, self, file_path)
        return dict (path = file_path)
    # end def _handle_file

    def _handle_resize (self, request, response, method, volume, path_spec) :
        req_data                = request.req_data
        path, dir, file         = path_spec
        self._is_image (volume, file)
        mode                    = req_data.get ("mode")
        file_name               = volume.abs_path (file)
        img                     = PIL.Image.open  (file_name)
        if mode   == "resize" :
            width               = int (req_data.get ("width",  "0"))
            height              = int (req_data.get ("height", "0"))
            img                 = img.resize ((width, height))
        elif mode == "crop" :
            x                   = int (req_data.get ("x",      "0"))
            y                   = int (req_data.get ("y",      "0"))
            width               = int (req_data.get ("width",  "0"))
            height              = int (req_data.get ("height", "0"))
            img                 = img.crop ((x, y, x + width, y + height))
        elif mode == "rotate" :
            angle   = int (req_data.get ("degree", "0"))
            bgcolor = "#ffffff"
            alpha   = PIL.Image.new ("RGBA", img.size, bgcolor)
            alpha.paste             (img)
            rotated = alpha.rotate \
                 ( angle    = 360 - angle
                 , resample = PIL.Image.BILINEAR
                 , expand   = True
                 )
            bg     = PIL.Image.new       ("RGBA", rotated.size, bgcolor)
            img    = PIL.Image.composite (rotated, bg, rotated)
        file.width, file.height = img.size
        img.save (file_name)
        return dict (changed = [volume.file_entry (dir, file)])
    # end def _handle_resize

    def _handle_rename (self, request, response, method, volume, path_spec) :
        path, dir, file = path_spec
        return dict \
            ( changed =
                [volume.rename (request.req_data.get ("name"), dir, file)]
            )
    # end def _handle_rename

    def _handle_mkdir (self, request, response, method, volume, path_spec) :
        path, dir, file         = path_spec
        if file :
            raise elFinder.Error ("errCmdParams")
        return dict \
            (added = [volume.mkdir (dir, request.req_data.get ("name"))])
    # end def _handle_mkdir

    def _handle_paste (self, request, response, method, volume, path_spec) :
        req_data            = request.req_data
        dvolume, dpath_spec = self.strip_volume (req_data ["dst"])
        svolume, spath_spec = self.strip_volume (req_data ["targets[]"])
        return svolume.copy \
            ( spath_spec, dvolume, dpath_spec
            , remove = int (req_data.get ("cut", "0"))
            )
    # end def _handle_paste

    def _handle_rm (self, request, response, method, volume, path_spec) :
        targets = request.req_data_list.get ("targets[]")
        removed = []
        for target in targets :
            volume, path_spec = self.strip_volume (target)
            removed.append (volume.remove (path_spec) ["hash"])
        return dict (removed = removed)
    # end def _handle_rm

    # _handle_ls
    # _handle_tmb
    # _handle_size
    # _handle_mkfile
    # _handle_duplicate
    # _handle_get
    # _handle_put
    # _handle_upload
    # _handle_archive
    # _handle_extract
    # _handle_search
    # _handle_info
    # _handle_netmount

    def _get_child (self, child, * grandchildren) :
        if child == "window" :
            return Window (* grandchildren, parent = self)
        return self.__super._get_child (child, * grandchildren)
    # end def _get_child

# end class Connector

if __name__ != "__main__" :
    GTW.RST.TOP.elFinder._Export ("*")
### __END__ GTW.RST.TOP.elFinder.Connector
