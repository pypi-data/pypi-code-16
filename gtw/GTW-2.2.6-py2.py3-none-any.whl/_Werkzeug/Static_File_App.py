# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.Werkzeug.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.Werkzeug.Static_File_App
#
# Purpose
#    WSGI application serving static files
#
# Revision Dates
#    22-Jun-2012 (CT) Creation
#    26-Jun-2012 (CT) Fix `__call__`
#     9-Jul-2012 (CT) Fix `get_path`
#    14-Oct-2015 (CT) Fix call to `zip.adler32` to pass `pyk.encoded`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                       import GTW
from   _TFL                       import TFL

import _GTW._Werkzeug
import _GTW._Werkzeug.Request
import _GTW._Werkzeug.Response

from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL.pyk                   import pyk

import _TFL._Meta.Object
import _TFL.Record
import _TFL.User_Config

from   datetime            import datetime

from   werkzeug            import exceptions
from   werkzeug.wsgi       import wrap_file
from   werkzeug.http       import is_resource_modified

import mimetypes
import os
import stat
import zlib

class Static_File_App (TFL.Meta.Object) :
    """WSGI application serving static files."""

    supported_methods = ("HEAD", "GET")

    def __init__ \
            ( self, dir_map
            , default_charset   = "utf-8"
            , default_mimetype  = "text/plain"
            , prefix            = ""
            , wrap              = exceptions.NotFound
            ) :
        self._dir_map           = dir_map
        self.default_charset    = default_charset
        self.default_mimetype   = default_mimetype
        self.prefix             = prefix.lstrip ("/")
        self.wrap               = wrap
    # end def __init__

    def __call__ (self, environ, start_response) :
        request    = GTW.Werkzeug.Request (environ)
        file_name  = self.get_path (request.path)
        if file_name and request.method in self.supported_methods :
            result = self._response (environ, request, file_name)
        else :
            result = self.wrap
        return result (environ, start_response)
    # end def __call__

    @Once_Property
    def dir_map (self) :
        result  = []
        add     = result.append
        _dm     = self._dir_map
        prefix  = self.prefix
        if isinstance (_dm, dict) :
            _dm = sorted (pyk.iteritems (_dm), reverse = True)
        for k, v in _dm :
            add (("/".join ((prefix, k)).lstrip ("/"), v))
        return tuple (result)
    # end def dir_map

    def file_info (self, file_name) :
        stat_result    = os.stat (file_name)
        mtime          = stat_result [stat.ST_MTIME]
        size           = stat_result [stat.ST_SIZE]
        last_modified  = datetime.fromtimestamp (mtime)
        offset         = TFL.user_config.time_zone.utcoffset (last_modified)
        last_modified -= offset
        fn_hash        = zlib.adler32 (pyk.encoded (file_name)) & 0xffffffff
        return TFL.Record \
            ( etag           = "sf-%s-%s-%s" % (mtime, size, fn_hash)
            , last_modified  = last_modified
            , content_length = size
            )
    # end def file_info

    def get_path (self, req_path) :
        req_path = req_path.lstrip ("/")
        for prefix, directory in self.dir_map :
            if (not prefix) or req_path.startswith (prefix) :
                path   = req_path [len (prefix): ].lstrip ("/")
                result = os.path.abspath (os.path.join (directory, path))
                if os.path.isfile (result) :
                    return result
                elif os.path.isdir (result) :
                    result = os.path.join (result, "index.html")
                    if os.path.isfile (result) :
                        return result
    # end def get_path

    def mimetype (self, file_name) :
        mimetype, encoding = mimetypes.guess_type (file_name)
        return \
            ( mimetype or self.default_mimetype
            , encoding or self.default_charset
            )
    # end def mimetype

    def _response (self, environ, request, file_name) :
        info         = self.file_info (file_name)
        has_changed  = is_resource_modified \
            (environ, info.etag, last_modified = info.last_modified)
        if has_changed :
            mimetype, encoding = self.mimetype (file_name)
            response = GTW.Werkzeug.Response \
                ( wrap_file (environ, open (file_name, "rb"))
                , direct_passthrough = True
                , mimetype           = mimetype
                )
            response.set_etag (info.etag)
            response.content_length  = info.content_length
            response.last_modified   = info.last_modified
            if encoding :
                response.charset     = encoding
        else :
            response = GTW.Werkzeug.Response (status = 304)
        return response
    # end def _response

    def __repr__ (self) :
        map = "; ".join ("%s -> %s" % (p or "/", d) for p, d in self.dir_map)
        return "<%s: %s>" % (self.__class__.__name__, map)
    # end def __repr__

# end class Static_File_App

if __name__ != "__main__" :
    GTW.Werkzeug._Export ("*")
else :
    import _TFL.CAO

    def dir_map (cmd) :
        from _TFL.predicate import rsplit_hst
        for d in cmd.argv :
            p, _, v = rsplit_hst (d, "=")
            yield p, v
    # end def dir_map

    def _main (cmd) :
        import werkzeug.serving
        app = Static_File_App (tuple (dir_map (cmd)), prefix = cmd.prefix or "")
        print ("Starting", app)
        werkzeug.serving.run_simple (cmd.hostname, cmd.port, app)
    # end def _main

    _Command = TFL.CAO.Cmd \
        ( handler       = _main
        , args          =
            ( "directory:S?Directory/ies to serve"
            ,
            )
        , opts          =
            ( "-hostname:S=localhost?Host for the application"
            , "-port:I=8888?Port to run the server on"
            , "-prefix:S?URL prefix of server"
            , TFL.CAO.Opt.Time_Zone ()
            )
        , min_args      = 1
        , description   =
            "Run a server on `-port` serving the files in `directory`"
        )

    _Command ()
### __END__ GTW.Werkzeug.Static_File_App
