# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.Graph.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.Graph.Command
#
# Purpose
#    Provide a command to generate renderings of MOM.Graphs
#
# Revision Dates
#    24-Sep-2012 (CT) Creation
#    13-Jun-2013 (CT) Remove `PNS_Aliases`
#     2-Sep-2014 (CT) Change `dynamic_defaults` to check `combined`
#    15-Sep-2015 (CT) Add option `-all`, automatic import of `import_XXX`
#    16-Sep-2015 (CT) Factor and DRY `render` (use `graph.render_to`)
#    16-Sep-2015 (CT) Factor `import_default`
#    15-Jun-2016 (CT) Rename handler argument `cmd` to `cao`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _MOM                       import MOM
from   _TFL                       import TFL

import _MOM.App_Type

from   _TFL                       import sos
from   _TFL._Meta.Once_Property   import Once_Property

import _TFL.Command
import _TFL.Decorator
import _TFL.Filename

class MOM_Graph_Command (TFL.Command.Root_Command) :
    """Command to generate renderings of MOM.Graphs"""

    _real_name              = "Command"

    min_args = max_args     = 0

    _opts                   = \
        ( "-all:B?Import all modules of package namespace"
        , "-dir:P?Directory of output file"
        , "-name:P?Name of output file"
        , "-png:B?Render graph as png file (implies `-svg`)"
        , "-svg:B?Render graph as svg file"
        , "-txt:B?Render graph as ascii graphic file"
        , "-verbose:B?Verbose output"
        )

    @Once_Property
    def app_type (self) :
        from _MOM._DBW._HPS.Manager import Manager as DBW
        from _MOM._EMS.Hash         import Manager as EMS
        apt = MOM.App_Type (self.PNS._._bname, self.PNS)
        return apt.Derived (EMS, DBW)
    # end def app_type

    @Once_Property
    def graph (self) :
        from _TFL.object_globals import object_globals
        globals = object_globals (self)
        return globals ["graph"]
    # end def graph

    def dynamic_defaults (self, defaults) :
        result   = self.__super.dynamic_defaults (defaults)
        combined = dict (defaults, ** result)
        if "dir" not in combined :
            result ["dir"] = self._app_dir_default
        if "name" not in combined :
            result ["name"] = self.PNS._._bname
        return result
    # end def dynamic_defaults

    def file_name (self, cao, ext) :
        fn = TFL.Filename ("." + ext, cao.name, default_dir = cao.dir)
        return fn.name
    # end def file_name

    def handler (self, cao) :
        if cao.all :
            self.import_all ()
        else :
            self.import_default ()
        g = self.graph (self.app_type)
        if cao.svg or cao.png :
            from _MOM._Graph.SVG import Renderer as SVG_Renderer
            self.render (cao, g, SVG_Renderer)
        if cao.png :
            import plumbum
            inkscape = plumbum.local [b"inkscape"]
            png_fn   = self.file_name (cao, "png")
            svg_fn   = self.file_name (cao, "svg")
            inkscape ["-y", "1", "-e", png_fn, svg_fn] ()
            if cao.verbose :
                print ("Rendered ", png_fn)
        if cao.txt :
            from _MOM._Graph.Ascii import Renderer as Ascii_Renderer
            self.render (cao, g, Ascii_Renderer)
    # end def handler

    def import_all (self) :
        self.PNS._Import_All ()
    # end def import_all

    def import_default (self) :
        PNS = self.PNS
        pn  = PNS.__name__.split (".") [-1]
        PNS._Import_Module ("_".join (("import", pn)))
    # end def import_default

    @TFL.Contextmanager
    def open (self, cao, ext) :
        fn = self.file_name (cao, ext)
        with open (fn, "wb") as f :
            yield f
    # end def open

    def render (self, cao, graph, Renderer) :
        with self.open (cao, Renderer.extension) as file :
            graph.render_to (file, Renderer)
            if cao.verbose :
                print ("Rendered ", file.name)
    # end def render

    def _app_dir_default (self) :
        return self.app_dir
    # end def _app_dir_default

Command = MOM_Graph_Command # end class

if __name__ != "__main__" :
    MOM.Graph._Export ("Command")
### __END__ MOM.Graph.Command
