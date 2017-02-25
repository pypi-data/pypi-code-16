# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package JNJ.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    JNJ.Templateer
#
# Purpose
#    Encapsulate Jinja template handling
#
# Revision Dates
#    14-Jan-2010 (CT) Creation
#    15-Jan-2010 (CT) `Error_Templates` added
#    18-Jan-2010 (CT) `get_std_template` added; s/Error_Templates/Template_Map/
#    29-Jan-2010 (CT) `get_template` changed to use `Template_Map`
#    19-Feb-2010 (CT) `error_405` added
#    14-May-2010 (MG) `dynamic_form` added
#    19-May-2010 (MG) `render_string` added
#     2-Aug-2010 (MG) `console` added
#    17-Aug-2010 (CT) `error_503` added
#    29-Dec-2010 (CT) `Template` added and used
#    31-Dec-2010 (CT) `Template_E` added and used
#     2-Jan-2011 (CT) `Template_E.get_CSS` added
#     3-Jan-2011 (CT) `Template_E.CSS` added
#     3-Jan-2011 (CT) `Template_E.get_CSS` changed to sort stylesheets by `rank`
#     4-Jan-2011 (CT) `templates_i` fixed (transitive `imports`)
#     5-Jan-2011 (CT) `templates_i` fixed (protect against recursive `imports`)
#     5-Jan-2011 (CT) `Template_E.__eq__` and `__hash__` added
#    14-Jan-2011 (CT) `get_CSS` replaced by `get_Media` (s/css/media/ -- mostly)
#    14-Jan-2011 (CT) `JS`, `JS_On_Ready`, `js_href`, `js_on_ready` and
#                     `scripts` added
#    16-Mar-2011 (CT) `Template_E.module`, `.get_macro`, and `.call_macro` added
#    16-Mar-2011 (CT) `Templateer.__init__` changed to pass `GTW` to
#                     `JNJ.Environment.HTML` -> `GTW.env` refers to `Templateer`
#    17-Mar-2011 (CT) `afs` and `e_type_afs` added
#    18-Mar-2011 (CT) `Template_E.parent` added and used in `get_macro`
#    31-May-2011 (CT) `render` changed to put `template` into `context`
#    15-Jun-2011 (MG) `get_css` added, `get_Media` and `_eval_fragments`
#                     changed to `classmethod`
#    27-Sep-2011 (MG) `s/CSS_Links/css_links/`, `s/JS_On_Ready/js_on_ready/`
#                     `js_on_ready` return the objects instead of the
#                     combined code
#                     `_eval_fragments`: use `scope.Eval`
#    24-Nov-2011 (CT) Add `Templateer.call_macro`
#     1-Dec-2011 (CT) Add `error_templates` and `error_template_names`
#    14-Dec-2011 (CT) Add `rel_links`
#     3-Jan-2012 (CT) Fix `js`
#     5-Jan-2012 (CT) Add `get_cached_media`, `Media_Map`, `_Media_[CR]`
#     9-Jan-2012 (CT) Fix `get_cached_media` (use `.scripts` unless `js_href`)
#    27-Jan-2012 (CT) Fix `__eq__` and `__hash__`,
#                     add `__lt__` and `totally_ordered`
#    29-Mar-2012 (CT) Rename `CSS_Parameters` to `Media_Parameters`
#    15-Apr-2012 (CT) Apply `sorted` to `injected` in `Templateer.get_template`
#    30-Apr-2012 (CT) Add `regatta_register_email`
#    10-May-2012 (CT) Add `error_email`
#     7-Jun-2012 (CT) Use `TFL.r_eval`, factor `env_globals`
#    22-Jun-2012 (CT) Use `static_handler.get_path` instead of home-grown code
#     6-Aug-2012 (CT) Add `etag`
#     6-Aug-2012 (CT) Remove `e_type_aggregator` (template doesn't exist)
#     8-Aug-2012 (CT) Add `e_type_doc`
#    25-Sep-2012 (CT) Add `pns_e_type_doc`
#     9-Oct-2012 (CT) Remove `account_activate`
#    11-Dec-2012 (CT) Add `error_410`
#     8-Jan-2013 (CT) Add `account_make_cert`
#    22-Jan-2014 (CT) Add `empty_dir`
#    12-Feb-2014 (CT) Add `regatta_ranking`
#    11-Mar-2014 (CT) Add `e_type_display`
#    15-Apr-2014 (CT) Add `media.script_files` to `Template_E.js`
#    24-Apr-2014 (CT) Add `afs_input`
#    24-Apr-2014 (CT) Add `mf3`, `mf3_input`, `mf3_v_seq`, `mf3_h_cols`
#     9-Jul-2014 (CT) Change `js` to use `pyk.decoded`, not home-grown code,
#                     to decode entries of `media.script_files`
#    29-Aug-2014 (CT) Remove `AFS` specific templates
#    12-Oct-2014 (CT) Add `sk` to `__lt__` to avoid Python-3 exception
#                     because different types
#    21-Jan-2015 (CT) Add `ETR_table`
#    11-Feb-2015 (CT) Factor `SRM` template declarations,
#                     remove obsolete templates
#    12-Jun-2015 (CT) Add `account_change_email_info`,
#                     `account_change_password_info`
#     2-Jun-2016 (CT) Add `e_type_selector`
#    11-Oct-2016 (CT) Import from `CHJ`, not `GTW`
#    30-Dec-2016 (CT) Allow scripts in template directories
#                     + Change `js` to try `env.loader.get_source`, too
#    ««revision-date»»···
#--

from   __future__  import unicode_literals

from   _JNJ               import JNJ
from   _TFL               import TFL
from   _TFL.pyk           import pyk

import _JNJ.Environment
import _JNJ.GTW

import _TFL._Meta.Object
import _TFL.Accessor
import _TFL.multimap
import _TFL.predicate
import _TFL.r_eval
import _TFL.Sorted_By

from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL._Meta.totally_ordered import totally_ordered
from   _TFL.Regexp                import *

from   jinja2.exceptions import TemplateNotFound

class _Template_ (TFL.Meta.Object) :
    """Describe a Jinja template."""

    def _init_ (self, name, path, media_fragment_name = None, parent_name = None) :
        assert name not in self.Map, name
        self.name                = name
        self.path                = path
        self.media_fragment_name = media_fragment_name
        self.parent_name         = parent_name
        self.id                  = len (self.Map)
        self.Map [name]          = self
    # end def _init_

    @property
    def args (self) :
        return self.name, self.path, self.media_fragment_name, self.parent_name
    # end def args

# end class _Template_

class Template (_Template_) :
    """Describe a Jinja template."""

    Map           = {}

    __init__      = _Template_._init_

# end class Template

@totally_ordered
class Template_E (_Template_) :
    """Describe a Jinja template for a specific Jinja environment."""

    Media_Map       = {}
    css_href_map    = {}

    _media_fragment = None
    _media_path     = None

    _coding_pat     = Regexp \
        ( r"^#\s*-\*-\s*coding:\s*[-a-zA-Z0-9]+\s*-\*-\s*" + "\n"
        )
    _extend_pat     = Regexp \
        ( r"\{\%-?\s*extends\s+(?P<name>.*?)\s*-?\%\}"
        )
    _import_pat     = Multi_Regexp \
        ( r"\{\%-?\s*import\s+"
          r"(?P<name>.*?)\s+"
          r"as\s+"
        , r"\{\%-?\s*from\s+"
          r"(?P<name>.*?)\s+"
          r"import\s+"
        , r"\{\%-\s*include\s+"
          r"(?P<name>.*?)\s+"
          r"(?:(?:ignore|with|without)\s+|-?\%\})"
        )

    _t_path         = None
    _t_source       = None

    def __new__ (cls, env, name, path = None, * args, ** kw) :
        if path in cls.By_Path :
            result = cls.By_Path [path]
        elif name in cls.Map :
            result = cls.Map     [name]
        else :
            if path is None :
                path = name
            result = _Template_.__new__ (cls)
            result._init_ (env, name, path, * args, ** kw)
        return result
    # end def __new__

    def _init_ (self, env, * args, ** kw) :
        self.env      = env
        self.injected = kw.pop ("injected", ())
        self._macros  = {}
        self.__super._init_ (* args, ** kw)
        if self.path not in self.By_Path :
            self.By_Path [self.path] = self
    # end def _init_

    @classmethod
    def copy (cls, env, proto) :
        return cls (env, * proto.args)
    # end def copy

    @Once_Property
    def CSS (self) :
        """Combined CSS rules required by media fragments that can
           loaded from a single file or included inline in a html <style>
           element.
        """
        return self.get_css (self._Media_R)
    # end def CSS

    @property
    def css_href (self) :
        return self.css_href_map.get (self.name)
    # end def css_href

    @Once_Property
    def css_links (self) :
        media = self._Media
        if media :
            return sorted (media.css_links, key = TFL.Getter.rank)
        return ()
    # end def css_links

    @Once_Property
    def env_globals (self) :
        return dict \
            (  (k, v) for k, v in pyk.iteritems (self.env.globals)
            if not k.startswith ("_")
            )
    # end def env_globals

    @Once_Property
    def extends (self) :
        env    = self.env
        pat    = self._extend_pat
        source = self.source
        if source and pat.search (source) :
            try :
                path = TFL.r_eval (pat.name.strip (), ** self.env_globals)
            except Exception :
                pass
            else :
                return self.__class__ (env, path)
    # end def extends

    @Once_Property
    def imports (self) :
        env    = self.env
        pat    = self._import_pat
        source = self.source
        if source :
            def _gen () :
                for match in pat.search_iter (source) :
                    try:
                        name   = match.group ("name").strip ()
                        pathes = TFL.r_eval  (name, ** self.env_globals)
                    except Exception :
                        pass
                    else :
                        if isinstance (pathes, pyk.string_types) :
                            pathes = [pathes]
                        for p in pathes :
                            yield self.__class__ (env, p)
            return list (_gen ())
        return []
    # end def imports

    @Once_Property
    def js (self) :
        """Combined Javascript code required by media fragments that can be
           loaded from a single file or included inline in a html <script>
           element.
        """
        env      = self.env
        encoding = env.encoding
        handler  = env.static_handler
        media    = self._Media_R
        if handler and media :
            def _gen (handler, encoding, scripts, media) :
                for s in sorted (scripts, key = TFL.Getter.rank) :
                    p = handler.get_path (s.src)
                    if p :
                        with open (p, "rb") as file :
                            yield file.read ().decode (encoding)
                    else :
                        try :
                            src, p, _ = env.loader.get_source (env, s.src)
                        except Exception :
                            pass
                        else :
                            if p :
                                yield src
                for s in sorted (media.script_files, key = TFL.Getter.rank) :
                    yield pyk.decoded (s.body, encoding)
            result = "\n\n".join \
                (TFL.uniq (_gen (handler, encoding, self.scripts_c, media)))
            return result
    # end def js

    @Once_Property
    def js_on_ready (self) :
        """Combined Javascript code required by media fragments to be
           executed when document is ready.
        """
        media = self._Media
        if media :
            return sorted (TFL.uniq (media.js_on_ready), key = TFL.Getter.rank)
        return ()
    # end def js_on_ready

    @Once_Property
    def media_fragment (self) :
        self._load_media ()
        return self._media_fragment
    # end def media_fragment

    @Once_Property
    def media_path (self) :
        self._load_media ()
        return self._media_path
    # end def media_path

    @Once_Property
    def module (self) :
        return self.template.module
    # end def module

    @Once_Property
    def parent (self) :
        if self.parent_name :
            return self.Map [self.parent_name]
    # end def parent

    @Once_Property
    def rel_links (self) :
        media = self._Media
        if media :
            return sorted (TFL.uniq (media.rel_links), key = TFL.Getter.rank)
        return ()
    # end def rel_links

    @Once_Property
    def scripts (self) :
        """Scripts required by media fragments that need to be put into
           separate <script src="..."> elements.
        """
        media = self._Media
        if media :
            return tuple (TFL.uniq (media.scripts))
        return ()
    # end def scripts

    @Once_Property
    def scripts_c (self) :
        """Scripts required by media fragments that can be cached."""
        media = self._Media_R
        if media :
            return tuple (s for s in TFL.uniq (media.scripts) if s.cache_p)
        return ()
    # end def scripts_c

    @Once_Property
    def scripts_x (self) :
        """Scripts required by media fragments that can not be cached."""
        media = self._Media_R
        if media :
            return tuple (s for s in TFL.uniq (media.scripts) if not s.cache_p)
        return ()
    # end def scripts_x

    @Once_Property
    def source (self) :
        self._load_template ()
        return self._t_source
    # end def source

    @Once_Property
    def source_path (self) :
        self._load_template ()
        return self._t_path
    # end def source_path

    @property
    def template (self) :
        return self.env.get_template (self.path)
    # end def template

    @Once_Property
    def templates (self) :
        return tuple (reversed (self.templates_e)) + self.templates_i
    # end def templates

    @Once_Property
    def templates_e (self) :
        def _gen () :
            yield self
            if self.extends :
                for e in self.extends.templates_e :
                    yield e
        return tuple (TFL.uniq (_gen ()))
    # end def templates_e

    @Once_Property
    def templates_i (self) :
        seen = set ([self])
        def _gen_i (imports) :
            for i in imports :
                if i not in seen :
                    yield i
                    seen.add (i)
                    for ii in _gen_i (i.imports) :
                        yield ii
        def _gen () :
            for e in reversed (self.templates_e) :
                for i in _gen_i (e.imports) :
                    yield i
            for i in _gen_i (self.injected) :
                yield i
        return tuple (_gen ())
    # end def templates_i

    @property
    def _Media (self) :
        result = self._Media_C
        if result is None :
            result = self._Media_R
        return result
    # end def _Media

    @property
    def _Media_C (self) :
        return self.Media_Map.get (self.name)
    # end def _Media_C

    @Once_Property
    def _Media_R (self) :
        return self.get_Media_R (self.env, self.templates)
    # end def _Media_R

    def call_macro (self, name, * _args, ** _kw) :
        macro = self.get_macro (name)
        return macro (* _args, ** _kw)
    # end def call_macro

    def get_cached_media (self, css_href, js_href) :
        from _CHJ.Media import Media
        if js_href :
            scripts = self.scripts_x + (js_href, )
        else :
            scripts = self.scripts
        result = Media \
            ( self.css_links
            , scripts
            , ("\n".join (pyk.decoded (x) for x in self.js_on_ready), )
            , self.rel_links
            )
        if css_href :
            self.css_href_map [self.name] = css_href
        return result
    # end def get_cached_media

    @classmethod
    def get_css (cls, media) :
        if media :
            return "\n\n".join \
                ( pyk.decoded (s) for s in
                    sorted (media.style_sheets, key = TFL.Getter.rank)
                )
    # end def get_css

    def get_macro (self, name) :
        result = self._macros.get (name)
        if result is None :
            result = getattr (self.module, name, None)
            if result is None :
                if self.parent :
                    result = self.parent.get_macro (name)
                else :
                    raise AttributeError (name)
            self._macros [name] = result
        return result
    # end def get_macro

    @classmethod
    def get_Media_R (cls, env, templates) :
        P = env.Media_Parameters
        media_fragment_pathes = tuple \
            (TFL.uniq (t.media_path for t in templates if t.media_path))
        if media_fragment_pathes :
            return cls._eval_fragments (media_fragment_pathes, P, env)
    # end def get_Media_R

    def render (self, context) :
        if "template" not in context :
            context.update (template = self)
        return self.template.render (context)
    # end def render

    @classmethod
    def _eval_fragments (cls, fragments, P, env = None) :
        from _CHJ import Parameters
        return Parameters.Scope (P, env).Eval (* fragments)
    # end def _eval_fragments

    def _load_media (self) :
        f_path = self.media_fragment_name
        if f_path is None :
            f_path = "%s.media" % (self.path.split ("::", 1) [-1], )
        try :
            source, path, _ = self.env.loader.get_source (self.env, f_path)
        except TemplateNotFound :
            pass
        else :
            self._media_fragment = self._coding_pat.sub ("", source, 1)
            self._media_path     = path
    # end def _load_media

    def _load_template (self) :
        try :
            source, path, _ = self.env.loader.get_source (self.env, self.path)
        except TemplateNotFound :
            pass
        else :
            self._t_path   = path
            self._t_source = source
    # end def _load_template

    def __eq__ (self, rhs) :
        return self.name == getattr (rhs, "name", rhs)
    # end def __eq__

    def __hash__ (self) :
        return hash (self.name)
    # end def __hash__

    def __lt__ (self, rhs) :
        sk = TFL.Sorted_By ()
        return sk (self.name) < sk (getattr (rhs, "name", rhs))
    # end def __lt__

    def __repr__ (self) :
        return "<JNJ.Template_E %s [%s]>" % (self.name, self.path)
    # end def __repr__

    def __str__ (self) :
        return "%s [%s]" % (self.name, self.path)
    # end def __str__

# end class Template_E

error_templates = \
    [ Template (400, "html/error_400.jnj")
    , Template (401, "html/error_401.jnj")
    , Template (403, "html/error_403.jnj")
    , Template (404, "html/error_404.jnj")
    , Template (405, "html/error_405.jnj")
    , Template (408, "html/error_408.jnj")
    , Template (410, "html/error_410.jnj")
    , Template (500, "html/error_500.jnj")
    , Template (503, "html/error_503.jnj")
    ]

Template ("account_change_email",         "html/change_email.jnj")
Template ("account_change_email_info",    "email/change_email_info.jnj")
Template ("account_change_password",      "html/change_password.jnj")
Template ("account_change_password_info", "email/change_password_info.jnj")
Template ("account_make_cert",            "html/make_client_cert.jnj")
Template ("account_register",             "html/register.jnj")
Template ("account_reset_password",       "html/reset_password.jnj")
Template ("account_reset_password_email", "email/reset_password.jnj")
Template ("account_verify_new_email",     "email/verify_new_email.jnj")
Template ("account_verify_email",         "email/verify_new_email.jnj")

Template ("mf3",           "html/mf3.m.jnj")
Template ("mf3_input",     "html/MF3/input.m.jnj")
Template ("mf3_h_cols",    "html/MF3/h_cols.m.jnj", parent_name = "mf3")

Template ("ETR_table",                    "html/ETR/table.m.jnj")

Template ("calendar",                     "html/calendar.jnj")
Template ("calendar_qx",                  "html/cal/wr.jnj")
Template ("calendar_day",                 "html/cal_day.jnj")
Template ("calendar_day_qx",              "html/cal/day.jnj")
Template ("calendar_week",                "html/cal_week.jnj")
Template ("console",                      "html/console.jnj")
Template ("default",                      "html/error.jnj")
Template ("empty_dir",                    "html/empty_dir.jnj")
Template ("error_email",                  "email/error.jnj")
Template ("e_type",                       "html/e_type.m.jnj")
Template ("e_type_admin",                 "html/e_type_admin.jnj")
Template ("e_type_display",               "html/e_type_display.jnj")
Template ("e_type_doc",                   "html/e_type_doc.jnj")
Template ("e_type_doc_bare",              "html/e_type_doc_bare.jnj")
Template ("e_type_mf3",                   "html/e_type_mf3.jnj")
Template ("e_type_selector",              "html/e_type_selector.m.jnj")
Template ("gallery",                      "html/gallery.jnj")
Template ("login",                        "html/login.jnj")
Template ("photo",                        "html/photo.jnj")
Template ("pns_e_type_doc",               "html/pns_e_type_doc.jnj")
Template ("site_admin",                   "html/site_admin.jnj")
Template ("video",                        "html/video.jnj")

class Templateer (TFL.Meta.Object) :
    """Encapsulate Jinja template handling"""

    Context = dict

    error_template_names = list (t.name for t in error_templates)

    def __init__ (self, * args, ** kw) :
        self.GTW = GTW = JNJ.GTW (self)
        self.env = env = JNJ.Environment.HTML (* args, GTW = GTW, ** kw)
        self.Template_Type = T = Template_E.New \
            ( "x"
            , By_Path      = {}
            , Map          = {}
            , Media_Map    = {}
            , css_href_map = {}
            , etag         = None
            )
        self.Template_Map  = T.Map
        for t in sorted (pyk.itervalues (Template.Map), key = TFL.Getter.id) :
            T.copy (env, t)
    # end def __init__

    @property
    def etag (self) :
        return self.Template_Type.etag
    # end def etag

    def call_macro (self, macro_name, * _args, ** _kw) :
        return self.GTW.call_macro (macro_name, * _args, ** _kw)
    # end def call_macro

    def get_template (self, name, injected = ()) :
        T      = self.Template_Type
        result = T (self.env, name)
        if injected :
            name_i = "%s|%s" % \
                ( result.name
                , "|".join (pyk.decoded (t.name) for t in sorted (injected))
                )
            if name_i in T.Map :
                result = T.Map [name_i]
            else :
                path   = result.path ### avoid lookup `T.By_Path [result.path]`
                args   = result.args [2:]
                result = T (self.env, name_i, None, * args, injected = injected)
                result.path = path
        return result
    # end def get_template

    def render (self, template_or_name, context) :
        template = template_or_name
        if isinstance (template_or_name, pyk.string_types) :
            template = self.get_template (template_or_name)
        return template.render (context)
    # end def render

    def render_string (self, template_string, context) :
        return self.env.from_string (template_string).render (context)
    # end def render_string

# end class Templateer

if __name__ != "__main__" :
    JNJ._Export ("*")
### __END__ JNJ.Templateer
