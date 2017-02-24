# -*- coding: utf-8 -*-
# Copyright (C) 2011-2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package CHJ.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    CHJ.Parameters
#
# Purpose
#    Support definition of parameters for media, i.e., CSS and JS, fragments
#
# Revision Dates
#    14-Jan-2011 (CT) Creation
#    13-Sep-2011 (CT) `Script_File` and `Style_File` added
#    13-Sep-2011 (MG) doctest added
#    27-Sep-2011 (MG) `Include`, `Eval`, and `_eval_file` added
#     3-Jan-2012 (CT) Add and use `_Media`, change `_MOB_.__call__` to not
#                     unnecessarily wrap media objects
#     8-Apr-2013 (CT) Add `chdir (base_dir)` to `__doc__`
#     8-Apr-2013 (CT) Add `Rule` and its children, `Rule_Definition`,
#                     factor `_Parameter_`
#    19-Sep-2013 (CT) Pass `AttributeError` to `TFL.Attr_Query`
#    20-Feb-2014 (CT) Add `Rule._resolved_children`
#     4-Apr-2014 (CT) Use `TFL.Q_Exp.Base`, not `TFL.Attr_Query ()`
#     9-Apr-2014 (CT) Pass `static_handler` to `GTW.CSS.Style_File`
#    15-Apr-2014 (CT) Fix `Script_File`, `script_files`
#    29-Oct-2015 (CT) Improve Python 3 compatibility
#    14-Jun-2016 (CT) Add `/media/GTW/js/V5a/form_field.js`
#    11-Oct-2016 (CT) Factor `TFL.Parameters`
#    11-Oct-2016 (CT) Move from `GTW` to `CHJ`
#    29-Dec-2016 (CT) Allow `Rule` instances as `P_dict` elements
#                     + Factor `_CHJ_Parameter_`
#                     + Redefine `P_dict`
#    16-Jan-2017 (CT) Add `_includes` guard to `Include`
#    17-Jan-2017 (CT) Redefine `Definition` to fix `Calc` instances with
#                     symbolic parameter values
#    20-Jan-2017 (CT) Add `Rule_Prefixed`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CHJ                       import CHJ
from   _TFL                       import TFL

from   _TFL._Meta.Property        import Lazy_Property
from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL.pyk                   import pyk
from   _TFL                       import sos
from   _TFL.Parameters            import \
    Definition, ddict, M_Definition, P, P_dict, _Parameter_

import _TFL._Meta.Object
import _TFL.Caller
import _TFL.Q_Exp

class Lazy_Calc (object) :
    """Property lazily computing a `Calc` expression"""

    def __init__ (self, name, calc_x, Calc) :
        self.name   = self.__name__ = name
        self.calc_x = calc_x
        self.Calc   = Calc
    # end def __init__

    def __get__ (self, obj, cls = None) :
        if obj is None :
            return self
        result = obj._resolved_calc (self.calc_x, self.Calc)
        setattr (obj, self.name, result)
        return result
    # end def __get__

# end class Lazy_Calc

class _CHJ_M_Definition_ (M_Definition) :

    def _setup_prop (cls, k, v, Q_Root, _nested_) :
        from _CHJ._CSS.Calc import Calc
        if isinstance (v, Calc) :
            setattr (cls, k, Lazy_Calc (k, v, Calc))
        else :
            return cls.__m_super._setup_prop (k, v, Q_Root, _nested_)
    # end def _setup_prop

# end class _CHJ_M_Definition_

class _CHJ_Definition_ \
        (TFL.Meta.BaM (Definition, metaclass = _CHJ_M_Definition_)) :

    def _resolved_calc (self, c, Calc) :
        Q_Root = TFL.Q_Exp.Q_Root
        def _resolved_args () :
            for a in c.args :
                if isinstance (a, Calc) :
                    a = self._resolved_calc (a, Calc)
                elif isinstance (a, Q_Root) :
                    a = a (self)
                yield a
        return c.__class__ (* tuple (_resolved_args ()))
    # end def _resolved_calc

Definition = _CHJ_Definition_ # end class

class _CHJ_Parameter_ (_Parameter_) :

    _real_name = "_Parameter_"

    def _resolved_kw (self, P, kw) :
        children = kw.get ("children")
        if children :
            kw ["children"] = list (self._resolved_children (P, children))
        return self.__super._resolved_kw (P, kw)
    # end def _resolved_kw

    def _resolved_children (self, P, children) :
        Q_Root = TFL.Q_Exp.Q_Root
        for c in children :
            if isinstance (c, Q_Root) :
                c = c (P)
            if isinstance (c, Rule) :
                c = c (P)
            yield c
    # end def _resolved_children

_Parameter_ = _CHJ_Parameter_ # end class

class _CHJ_P_dict_ (_Parameter_, P_dict) :

    _real_name = "P_dict"

P_dict = _CHJ_P_dict_ # end class

class Rule (_Parameter_) :
    """Parameterized CSS rule"""

    def __call__ (self, P) :
        from _CHJ._CSS import Rule as CSS_Rule
        RT       = getattr (CSS_Rule, self.__class__.__name__)
        args     = tuple (self._resolved_args (P, self.args))
        kw       = dict  (self._resolved_kw   (P, self.kw))
        return RT (* args, ** kw)
    # end def __call__

# end class Rule

class Rule_Attr     (Rule) : pass
class Rule_Child    (Rule) : pass
class Rule_Class    (Rule) : pass
class Rule_Pseudo   (Rule) : pass
class Rule_Sibling  (Rule) : pass

class Rule_Prefixed (Rule) :

    def __init__ (self, prefix, * selectors, ** declarations) :
        declarations.update   (prefix = prefix)
        self.__super.__init__ (* selectors, ** declarations)
    # end def __init__

# end class Rule_Prefixed

class Rule_Definition (Definition) :
    """Definition of parameterized CSS rules"""

# end class Rule_Definition

class _Parameters_Scope_ (TFL.Caller.Object_Scope_Mutable) :
    """Encapsulate media parameters so that it is usable as context for
       `exec` of a file containing media fragments.
    """

    _real_name = "Scope"

    class _MOB_ (TFL.Meta.Object) :
        """Wrapper for media object class"""

        def __init__ (self, cls, ext = None, ** kw) :
            self._cls = cls
            self._    = self
            self._ext = ext if ext is not None else []
            self._kw  = kw
        # end def __init__

        def __call__ (self, * args, ** kw) :
            cls = self._cls
            ckw = dict (self._kw, ** kw)
            if len (args) == 1 and (isinstance (args [0], cls)) and not ckw :
                result = args [0]
            else :
                result = cls (* args, ** ckw)
            self._ext.append (result)
            return result
        # end def __call__

        def __getattr__ (self, name) :
            return getattr (self._cls, name)
        # end def __getattr__

    # end class _MOB_

    @pyk.adapt__str__
    class _Script_File_ (TFL.Meta.Object) :
        """Wrapper for a javascript `Script_File` referenced in a media fragment."""

        cache_p       = True
        requires      = ()
        may_cache     = True

        def __init__ (self, file_name, body = None, rank = 0) :
            self.file_name = file_name
            self._body     = body
            self.rank      = 0
        # end def __init__

        @property
        def body (self) :
            result = self._body
            if result is None :
                fn = self.file_name
                with open (fn, "rb") as f :
                    result = self._body = \
                        pyk.decoded (f.read ().strip (), "utf-8", "iso-8859-1")
            return result
        # end def body

        def __str__ (self) :
            return self.body
        # end def __str__

    # end class _Script_File_

    css_links            = property (lambda s : s._Media.css_links)
    js_on_ready          = property (lambda s : s._Media.js_on_ready)
    rel_links            = property (lambda s : s._Media.rel_links)
    scripts              = property (lambda s : s._Media.scripts)
    style_sheets         = property (lambda s : s.Style_Sheet._ext)

    def __init__ (self, parameters, env = None) :
        from _CHJ._CSS  import import_CSS
        from _CHJ.Media import CSS_Link, JS_On_Ready, Rel_Link, Script
        self.P                = parameters
        self.CSS_Link         = self._MOB_ (CSS_Link)
        self.JS_On_Ready      = self._MOB_ (JS_On_Ready)
        self.Rel_Link         = self._MOB_ (Rel_Link)
        self.Script           = self._MOB_ (Script)
        self.Style_Sheet = SS = self._MOB_ (import_CSS.Style_Sheet)
        self.Style_File       = self._MOB_ \
            ( import_CSS.Style_File, SS._ext
            , static_handler = env.static_handler
            )
        self.env              = env
        self.script_files     = []
        self._includes        = set ()
        self.__super.__init__ \
            ( object = import_CSS
            , locls  = dict (Include = self.Include)
            )
        self._setup_media ()
    # end def __init__

    def Eval (self, * fragments) :
        self.globs = {}
        for f in fragments :
            self._eval_file (f)
        self._setup_media ()
        return self
    # end def Eval

    def Include (self, * includes, ** kw) :
        ignore_missing = kw.pop ("ignore_missing", False)
        assert not kw, kw
        env            = self.env
        get_source     = env.loader.get_source
        for fn in includes :
            if not fn.endswith (".media") :
                fn = "%s.media" % (fn, )
            source, path, _ = get_source (env, fn)
            if path not in self._includes :
                self._includes.add (path)
                self._eval_file    (path)
    # end def Include

    def Script_File (self, src, ** kw) :
        env  = self.env
        body = None
        if sos.path.isfile (src) :
            fn      = src
        else :
            handler = env.static_handler
            fn      = handler.get_path (src) if handler else None
            if fn is None :
                body, fn, _ = env.loader.get_source (env, src)
        sf   = self._Script_File_ (fn, body, ** kw)
        self.script_files.append  (sf)
    # end def Script_File

    def _eval_file (self, filename) :
        with open (filename, "rt") as file :
            self.globs ["__name__"] = filename
            exec (file.read (), self.globs, self)
    # end def _eval_file

    def _setup_media (self) :
        from _CHJ.Media import Media
        self._Media = Media \
            ( self.CSS_Link._ext
            , self.Script._ext
            , self.JS_On_Ready._ext
            , self.Rel_Link._ext
            )
    # end def _setup_media

    def __getitem__ (self, index) :
        try :
            if (   isinstance (index, pyk.string_types)
               and not index.startswith ("_")
               ) :
                return getattr (self, index)
        except AttributeError :
            return self.__super.__getitem__ (index)
    # end def __getitem__

Scope = _Parameters_Scope_ # end class

__doc__ = r"""
    >>> from _JNJ.Media_Defaults import Media_Defaults
    >>> from _JNJ.Environment    import HTML
    >>> import _GTW.jQuery
    >>> import os
    >>> base_dir        = os.path.abspath \
    ...    (os.path.join (os.path.dirname (__file__), "..", "_GTW", "__test__"))
    >>> env             = HTML (load_path = base_dir)
    >>> base_media      = os.path.join (base_dir, "_test.media")
    >>> os.chdir (base_dir)

    >>> def as_string (fragments) :
    ...     return "\n\n".join \
    ...         (str (s) for s in sorted (fragments, key = TFL.Getter.rank))

    >>> scope = Scope (Media_Defaults, env).Eval (base_media)
    >>> print (as_string (scope.style_sheets))
    a, abbr, acronym, address, article, aside, audio
      { border         : 0
      ; font           : inherit
      ; font-size      : 100%
      ; margin         : 0
      ; outline        : 0
      ; padding        : 0
      ; vertical-align : baseline
      }
    <BLANKLINE>
    /* --> rules from a existing CSS file `/
    a.hide
    {
        display:          none
    }
    /* <-- */
    >>> print (as_string (scope.script_files))
    /* a test javascript file directly included */

    >>> list (scope.scripts)
    [/media/GTW/js/jquery.js: text/javascript, /media/GTW/js/jquery-ui.js: text/javascript, /media/GTW/js/V5a/V5a.js: text/javascript, /media/GTW/js/GTW.js: text/javascript, /media/GTW/js/GTW/jQ/button_pure.js: text/javascript, /media/GTW/js/V5a/history_test.js: text/javascript, /media/GTW/js/V5a/history_push.js: text/javascript, /media/GTW/js/GTW/util.js: text/javascript, /media/GTW/js/GTW/jQ/util.js: text/javascript, /media/GTW/js/GTW/jQ/autocomplete.js: text/javascript, /media/GTW/js/V5a/form_field.js: text/javascript, /media/GTW/js/GTW/jQ/e_type_selector.js: text/javascript, /media/GTW/js/GTW/L.js: text/javascript, /media/GTW/js/GTW/jQ/mf3.js: text/javascript]

    >>> list (scope.css_links)
    [all: /media/GTW/css/jquery.gritter.css]

    >>> list (scope.rel_links)
    [href="/media/GTW/css/jquery.gritter.rel.css"]

    >>> print (as_string (scope.js_on_ready))
    /* this is a JS on ready code */;

"""

if __name__ != "__main__" :
    CHJ._Export_Module ()
### __END__ CHJ.Parameters
