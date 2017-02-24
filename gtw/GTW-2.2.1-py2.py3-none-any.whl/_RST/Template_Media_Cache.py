# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.Template_Media_Cache
#
# Purpose
#    Cache media fragments for templates
#
# Revision Dates
#    24-Jul-2012 (CT) Creation (ported from GTW.NAV)
#     5-Aug-2012 (MG) Cache filenames of media fragments
#     5-Aug-2012 (MG) Fix filename cache (use `templates` instead of
#                     `templates_i` )
#     6-Aug-2012 (CT) Add `etag`
#    10-Aug-2012 (CT) Add `verbose`
#    14-Aug-2012 (MG) Consider `Media_Base.Domain` for href creation
#    17-Aug-2012 (MG) Set `etag`during cache creation
#     2-May-2013 (CT) Use `root.hash_fct` and `root.b64_encoded`
#    18-Nov-2013 (CT) Change default `input_encoding` to `utf-8`
#    15-Apr-2014 (CT) Always create `js` cache to include `Script_File`
#    12-Oct-2014 (CT) Use `TFL.Secure_Hash`
#    19-Nov-2015 (CT) Change `_create_cache` to delete existing cached files
#    11-Oct-2016 (CT) Use `CHJ.Media`, not `GTW.Media`
#    ««revision-date»»···
#--

from   __future__             import print_function

from   _CHJ                   import CHJ
from   _GTW                   import GTW
from   _TFL                   import TFL

import _GTW._RST
import _CHJ.Media

from   _TFL.pyk               import pyk
from   _TFL                   import sos

import _TFL._Meta.Object
import _TFL.predicate

from   posixpath import join as pp_join

class Template_Media_Cache (TFL.Meta.Object) :

    cache_rank = 1000

    def __init__ \
            ( self, media_dir, prefix
            , clear_dir       = False
            , cache_filenames = False
            , verbose         = False
            ) :
        if not prefix.startswith ("/") :
            prefix           = "/%s" % (prefix, )
        if CHJ.Media_Base.Domain :
            prefix           = "".join ((CHJ.Media_Base.Domain, prefix))
        self.media_dir       = media_dir
        self.prefix          = prefix
        self.clear_dir       = clear_dir
        self.cache_filenames = cache_filenames
        self.filenames       = set ()
        self.templates_seen  = set ()
        self.verbose         = verbose
    # end def __init__

    def as_pickle_cargo (self, root) :
        if self.clear_dir :
            self._clear_dir ()
        css_map = {}
        js_map  = {}
        t_set   = set ()
        TEST    = root.TEST
        TT      = root.Templateer.Template_Type
        for t in TFL.uniq (root.template_iter ()) :
            t_set.update (t.templates)
            css_href = self._add_to_map (root, t, "CSS",   css_map)
            js_href  = self._add_to_map (root, t, "js", js_map)
            TT.Media_Map [t.name] = t.get_cached_media (css_href, js_href)
            if self.cache_filenames :
                self._add_filenames (t)
        self._create_cache ("CSS", css_map, None if TEST else CHJ.minified_css)
        self._create_cache ("js",  js_map,  None if TEST else CHJ.minified_js)
        TT.etag = self._get_etag (root, css_map, js_map, t_set)
        return dict \
            ( css_href_map = TT.css_href_map
            , etag         = TT.etag
            , Media_Map    = TT.Media_Map
            )
    # end def as_pickle_cargo

    def _add_filenames (self, template) :
        if template not in self.templates_seen :
            self.templates_seen.add (template)
            if template.source_path :
                self.filenames.add (template.source_path)
            if template.media_path :
                self.filenames.add (template.media_path)
            for it in template.templates :
                self._add_filenames (it)
    # end def _add_filenames

    def from_pickle_cargo (self, root, cargo) :
        TT              = root.Templateer.Template_Type
        TT.css_href_map = cargo.get ("css_href_map", {})
        TT.etag         = cargo.get ("etag")
        TT.Media_Map    = cargo.get ("Media_Map",    {})
    # end def from_pickle_cargo

    def _add_to_map (self, root, t, name, map) :
        try :
            attr = getattr (t, name)
        except Exception as exc :
            print (name, "exception for template", t.path)
            print ("   ", exc)
            if __debug__ :
                import traceback
                traceback.print_exc ()
        else :
            if attr :
                attr = attr.encode (t.env.encoding)
                k    = pyk.decoded \
                    (root.hash_fct (attr).b64digest (strip = True))
                if k not in map :
                    cn      = ".".join      ((k, name.lower ()))
                    href    = pp_join       (self.prefix,    cn)
                    fn      = sos.path.join (self.media_dir, cn)
                    map [k] = (href, fn, attr)
                else :
                    href = map [k] [0]
                return href
    # end def _add_to_map

    def _clear_dir (self) :
        for fod in sos.listdir_full (self.media_dir) :
            if sos.path.isdir (fod) :
                sos.rmdir  (fod, True)
            else :
                sos.unlink (fod)
    # end def _clear_dir

    def _create_cache (self, name, map, minifier = None) :
        media_dir = self.media_dir
        if not sos.path.isdir (media_dir) :
            sos.mkdir_p (media_dir)
        else :
            for f in sos.listdir_ext (media_dir, name.lower ()) :
                sos.remove (f)
        for k, (href, fn, attr) in pyk.iteritems (map) :
            with open (fn, "wb") as file :
                if minifier is not None :
                    attr = minifier (attr)
                file.write (attr)
                if self.verbose :
                    print ("Wrote template media cache file", fn)
    # end def _create_cache

    def _get_etag (self, root, css_map, js_map, t_set) :
        def _gen (css_map, js_map, t_set) :
            yield "CSS"
            for c in sorted (css_map) :
                yield c
            yield "JS"
            for j in sorted (js_map) :
                yield j
            yield "JNJ"
            for t in sorted (t_set, key = TFL.Getter.path) :
                s = t.source
                if s is not None :
                    yield s
        result = root.hash_fct \
            (tuple (_gen (css_map, js_map, t_set))).b64digest ()
        return result
    # end def _get_etag

    def __str__ (self) :
        return "Template_Media_Cache (%r, %r)" % (self.media_dir, self.prefix)
    # end def __str__

# end class Template_Media_Cache

if __name__ != "__main__" :
    GTW.RST._Export ("*")
### __END__ GTW.RST.Template_Media_Cache
