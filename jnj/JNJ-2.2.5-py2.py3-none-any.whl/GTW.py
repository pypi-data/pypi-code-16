# -*- coding: utf-8 -*-
# Copyright (C) 2009-2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    JNJ.GTW
#
# Purpose
#    Provide additional global functions for Jinja templates
#
# Revision Dates
#    29-Dec-2009 (CT) Creation
#    13-Jan-2010 (CT) Converted to class; `call_macro` added;
#                     `_T` and `_Tn` added to class `GTW`
#    25-Jan-2010 (MG) `_T` and `_Tn` need to be static methods
#    27-Jan-2010 (CT) `Getter`, `now`, and `sorted` added
#    17-Feb-2010 (CT) `email_uri`, `obfuscated`, `tel_uri`, and `uri` added
#    23-Feb-2010 (CT) `pjoin` added
#    24-Feb-2010 (CT) `log_stdout` added
#    10-Mar-2010 (CT) `zip` added
#     3-May-2010 (MG) `call_macro`: `widget_type` added
#     5-May-2010 (MG) `render_fofi_widget` added
#     5-May-2010 (MG) `default_render_mode` used
#     5-May-2010 (MG) `render_mode` added
#     6-May-2010 (MG) `render_fofi_widget` exception handling improoved
#     3-Aug-2010 (CT) Use `HTML.obfuscator` instead of home-grown code
#     3-Aug-2010 (CT) `obfuscated` removed
#    20-Sep-2010 (CT) `Sorted_By` added
#    22-Sep-2010 (CT) `eval_sorted_by` added
#     8-Oct-2010 (CT) `len` added
#    23-Nov-2010 (CT) `list` and `reversed` added
#    27-Nov-2010 (CT) `formatted` added
#    18-Mar-2011 (CT) `get_macro` changed to use `Template_E.get_macro`
#    22-Mar-2011 (CT) `dict` added
#    30-Nov-2011 (CT) Add `filtered_join`
#    30-Nov-2011 (CT) Add `dir` and `getattr`
#     1-Dec-2011 (CT) Add `styler`
#    18-Jan-2012 (CT) Add `attr_join`
#    27-Jan-2012 (CT) Change `email_uri` to allow tuple argument for `email`
#    22-Feb-2012 (CT) Add `vimeo_video` and `youtube_video`
#     4-May-2012 (CT) Change `email_uri` to allow email-tuple and `text` passed
#    16-Jul-2012 (MG) `log_stdout` enhanced
#     6-Aug-2012 (MG) Add `update_blackboard`
#     8-Aug-2012 (MG) Remove debug code
#     9-Aug-2012 (MG) Use `** kw` notation for `update_blackboard`
#    12-Feb-2014 (CT) Add `enumerate`
#    13-Feb-2014 (CT) Add `Dingbats` and `unichr`
#    14-Mar-2014 (CT) Add `any` and `all`
#    10-Apr-2014 (CT) Add `first`
#    14-Apr-2014 (CT) Add `ichain`
#    18-Apr-2014 (CT) Add `bool`
#     2-Dec-2014 (CT) Add `setattr`
#    21-Jan-2015 (CT) Add `filtered_dict`
#    23-Jan-2015 (CT) Add `html_char_ref`
#    10-Jun-2015 (CT) Add `uuid`
#    13-Nov-2015 (CT) Define `dir`, `setattr` as functions to avoid sphinx errors
#    16-May-2016 (CT) Add `xmlattr`
#    16-May-2016 (CT) Add guard for `Undefined` to `filtered_dict`
#    11-Oct-2016 (CT) Change `GTW.HTML` to `TFL.HTML`
#    14-Nov-2016 (CT) Add `isinstance`, `pyk`
#    19-Jan-2017 (CT) Add `split_hst`
#    ««revision-date»»···
#--

from   __future__               import print_function

from   _JNJ                     import JNJ
from   _TFL                     import TFL

from   _TFL.I18N                import _, _T, _Tn
from   _TFL.predicate           import filtered_join, split_hst
from   _TFL.pyk                 import pyk
from   _TFL                     import sos

from   _TFL._Meta.Once_Property import Once_Property

import _TFL._Meta.Object
import _TFL.Accessor
import _TFL.Caller
import _TFL.HTML
import _TFL.Sorted_By

import itertools
import uuid

class GTW (TFL.Meta.Object) :
    """Provide additional global functions for Jinja templates."""

    from jinja2.runtime import Undefined

    def __init__ (self, env) :
        import _JNJ.Templateer ### used by `get_macro`
        self.env               = env
        self.render_mode_stack = []
    # end def __init__

    all  = staticmethod (all)
    any  = staticmethod (any)
    bool = staticmethod (bool)

    @Once_Property
    def Dingbats (self) :
        """Provide access to :mod:`~_TFL.Dingbats`."""
        from _TFL import Dingbats
        return Dingbats
    # end def Dingbats

    def attr_join (self, sep, objects, attr_name) :
        """Join the values of attribute `attr_name` of `objects` by `sep`."""
        def _gen (objects, attr_name) :
            for o in objects :
                a = getattr (o, attr_name)
                if a :
                    yield a
        return sep.join (_gen (objects, attr_name))
    # end def attr_join

    def call_macro (self, macro_name, * _args, ** _kw) :
        """Call macro named by `macro_name` passing `* _args, ** _kw`."""
        templ_name  = _kw.pop ("templ_name",  None)
        widget_type = _kw.pop ("widget_type", None)
        try :
            macro  = self.get_macro (macro_name, templ_name, widget_type)
        except ValueError :
            print (repr ((macro_name, templ_name, _args, _kw)))
            raise
        return macro (* _args, ** _kw)
    # end def call_macro

    dict = staticmethod (dict)

    def dir (self, x = None) :
        """Return directory of `x` or the locals of the caller."""
        if x is None :
            return sorted (TFL.Caller.locals ())
        else :
            return dir (x)
    # end def dir

    def email_uri (self, email, text = None, ** kw) :
        """Returns a mailto URI for `email`.

           http://tools.ietf.org/html/rfc3966
        """
        if isinstance (email, tuple) :
            email, email_text = email
        if text is None :
            text = email_text
        return self.uri (scheme = "mailto", uri = email, text = text, ** kw)
    # end def email_uri

    enumerate = staticmethod (enumerate)

    def eval_sorted_by (self, key = None) :
        """Returns a function that can be passed to `Sorted_By` to evaluate
           the `sorted_by` attribute of an object, If `key` is passed in, the
           `sorted_by` attribute of the attribute referred to by `key` will
           be evaluated.
        """
        if key is None :
            result = lambda obj : obj.sorted_by (obj)
        else :
            getter = getattr (TFL.Getter, key)
            def result (obj) :
                v = getter (obj)
                return v.sorted_by (v)
        return result
    # end def eval_sorted_by

    def filtered_dict (self, * ds, ** kw) :
        """Return a dict will all non-empty values of `ds` and `kw`."""
        Undef  = self.Undefined
        result = {}
        for d in ds :
            result.update (d)
        result.update (kw)
        return dict \
            (  (k, v) for k, v in pyk.iteritems (result)
            if v is not None and v != "" and not isinstance (v, Undef)
            )
    # end def filtered_dict

    filtered_join = staticmethod (filtered_join)
    first         = staticmethod (TFL.first)

    def firstof (self, * args) :
        """Return the first non-None and non-Undefined value of `args`.

           If `args` contains a single `tuple` or `list`, returns first
           non-None and non-Undefined element of that sequence.
        """
        if len (args) == 1 and isinstance (args [0], (tuple, list)) :
            args = args [0]
        for a in args :
            if not (a is None or isinstance (a, self.Undefined)) :
                return a
    # end def firstof

    def formatted (self, format, * args, ** kw) :
        """Return result of `%` applied to `format`and `args` or `kw`."""
        if args :
            assert not kw
            return format % args
        else :
            return format % kw
    # end def formatted

    def get_macro (self, macro_name, templ_name = None, widget_type = None) :
        """Return macro `macro_name` from template `templ_name`."""
        if widget_type :
            macro_name = getattr (macro_name, widget_type)
        if not isinstance (macro_name, pyk.string_types) :
            macro_name = str (macro_name)
        if templ_name is None :
            templ_name, macro_name = \
                (p.strip () for p in macro_name.split (",", 1))
        template = self.env.get_template (templ_name)
        if isinstance (template, JNJ.Template_E) :
            result = template.get_macro (macro_name)
        else :
            result = getattr (template.module, macro_name)
        return result
    # end def get_macro

    getattr    = staticmethod (getattr)
    Getter     = TFL.Getter

    def html_char_ref (self, arg) :
        """Return HTML character reference for `arg`."""
        if isinstance (arg, pyk.string_types) and len (arg) == 1 :
            arg = ord (arg)
        return "&#x%4.4X" % (arg, )
    # end def html_char_ref

    ichain     = staticmethod (itertools.chain)
    isinstance = staticmethod (isinstance)
    len        = staticmethod (len)
    list       = staticmethod (list)

    def log_stdout (self, * text) :
        """Write `text` to standard output."""
        print (* text)
        return ""
    # end def log_stdout

    def now (self, format = "%Y/%m/%d") :
        """Return the current date-time formatted by `format`."""
        from datetime import datetime
        result = datetime.now ()
        return result.strftime (format)
    # end def now

    pjoin      = staticmethod (sos.path.join)
    pyk        = pyk

    def render_fofi_widget (self, fofi, widget, * args, ** kw) :
        pushed          = False
        obj_render_mode = getattr (fofi, "render_mode", None)
        kw_render_mode  = kw.pop  ("render_mode",       None)
        if obj_render_mode :
            pushed      = True
            self.render_mode_stack.append (obj_render_mode)
        elif kw_render_mode :
            pushed      = True
            self.render_mode_stack.append (kw_render_mode)
        elif not self.render_mode_stack :
            pushed      = True
            self.render_mode_stack.append (fofi.default_render_mode)
        render_mode     = self.render_mode_stack [-1]
        try :
            try :
                mode_desc = fofi.render_mode_description [render_mode]
            except ValueError :
                raise ValueError \
                    ("%r does not support render mode %r" % (fofi, render_mode))
            result      = self.call_macro \
                (getattr (mode_desc, widget), * args, ** kw)
            return result
        finally :
            if pushed :
                self.render_mode_stack.pop ()
    # end def render_fofi_widget

    @Once_Property
    def render_mode (self) :
        return self.render_mode_stack and self.render_mode_stack [-1]
    # end def render_mode

    reversed   = staticmethod (reversed)

    def setattr (self, x, y, v) :
        """Set attribute `y` of object `x` to value `v`."""
        setattr (x, y, v)
    # end def setattr

    sorted     = staticmethod (sorted)
    Sorted_By  = TFL.Sorted_By
    split_hst  = staticmethod (split_hst)
    styler     = staticmethod (TFL.HTML.Styler)

    def tel_uri (self, phone_number, text = None, ** kw) :
        """Returns a telephone URI for `phone_number`.

           http://tools.ietf.org/html/rfc3966
        """
        return self.uri (scheme = "tel", uri = phone_number, text = text, ** kw)
    # end def tel_uri

    def update_blackboard (self, ** kw) :
        """Add `kw` to blackboard."""
        self.blackboard.update (kw)
        return ""
    # end def update_blackboard

    unichr = staticmethod (pyk.unichr)

    def uri (self, scheme, uri, text = None, ** kw) :
        """Return HTML <a> element as specified by `scheme`, `uri`, `text`, and
           `kw`.

           If `kw` contains a true value for `obfuscate`,
           :func:`~_TFL.HTML.obfuscator` will be applied to the result.

           All other values in `kw` will be converted to attributes of the <a>
           element.
        """
        obfuscate = kw.pop ("obfuscate", False)
        if text is None :
            text = uri
        attrs = ['href="%s:%s"' % (scheme, uri)]
        for k, v in pyk.iteritems (kw) :
            attrs.append ('%s="%s"' % (k, v))
        attrs = " ".join (sorted (attrs))
        result = u"""<a %(attrs)s>%(text)s</a>""" % locals ()
        if obfuscate :
            result = TFL.HTML.obfuscator [scheme] (result)
        return result
    # end def uri

    def uuid (self) :
        """Return the hex-value of a newly created UUID (uuid1)."""
        return uuid.uuid1 ().hex
    # end def uuid

    vimeo_video   = staticmethod (TFL.HTML.vimeo_video)
    youtube_video = staticmethod (TFL.HTML.youtube_video)

    def xmlattr (self, * ds, ** kw) :
        """Convert (sorted) items of dict `d` to SGML/XML attribute string.

           This is similar to jinja's `xmlattr` filter but ensures
           deterministic output by sorting by attribute name.
        """
        from jinja2.utils import escape
        d      = self.filtered_dict (* ds, ** kw)
        result = " ".join \
            ( '%s="%s"' % (escape (k), escape (v))
            for k, v in sorted (pyk.iteritems (d), key = TFL.Getter [0])
            )
        return (" " + result) if result else ""
    # end def xmlattr

    zip           = staticmethod (zip)
    _T            = staticmethod (_T)
    _             = staticmethod (_)
    _Tn           = staticmethod (_Tn)

# end class GTW

if __name__ != "__main__" :
    JNJ._Export ("GTW")
### __END__ JNJ.GTW
