# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.TOP.MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.TOP.MOM.Field
#
# Purpose
#    Define classes for displaying E_Type attributes as fields
#
# Revision Dates
#    20-Aug-2014 (CT) Creation
#    23-Jan-2015 (CT) Use `aq._ui_name_short_T`, not `aq._ui_name_T`
#    23-Jan-2015 (CT) Change `as_html` to assume a `MOM.Id_Entity` argument
#    23-Jan-2015 (CT) Add and use `_value_getter`
#    23-Jan-2015 (CT) Add `css_class_add`, factor `css_align`
#    27-Jan-2015 (CT) Change args of `Attr.__init__` to `resource, field_name`
#    27-Jan-2015 (CT) Add `Id_Entity_List`, `Id_Entity_Set`,
#                     `Id_Entity_Collection_Size`
#    27-Jan-2015 (CT) Rename `Link` to `HTML_Link`
#     2-Feb-2015 (CT) Add `Attr_Set_M`, factor `Base`
#     3-Feb-2015 (CT) Add `Attr_Set_1`, `Attr_Set_R`; add `as_html_iter`
#     3-Feb-2015 (CT) Remove argument `v` from `as_html`
#     3-Feb-2015 (CT) Add `css_class_dyn`
#     4-Feb-2015 (CT) Add argument `renderer` to `as_html`, `value`
#     4-Feb-2015 (CT) Add `Index`
#    14-May-2015 (CT) Add guard for `is_undefined` to property `attr`
#    14-May-2015 (CT) Add `HTML_Link_Set.max_links`
#    22-Jun-2015 (CT) Change `_set_as_html` to avoid empty elements
#                     (use `&nbsp;` in place of nothing)
#    24-Jun-2015 (CT) Add `zero_width_space` to `Creation.as_html`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    19-Oct-2016 (CT) Add missing `renderer` arg to `_set_as_html`
#    19-Oct-2016 (CT) Change `Base.value` to let `FO` resolve dotted names
#                     * needed for structured attributes
#     4-Nov-2016 (CT) Fix `Attr_Set_R.as_html`
#                     + add missing `renderer`to call of `_set_as_html`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                     import GTW
from   _MOM                     import MOM
from   _TFL                     import TFL

from   _MOM.import_MOM          import Q

import _MOM.Entity
import _MOM._Attr.Type

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL._Meta.Property      import Alias_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.Dingbats            import zero_width_space
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.predicate           import filtered_join
from   _TFL.pyk                 import pyk
from   _TFL.Undef               import is_undefined

import _TFL._Meta.Object
import _TFL.Accessor
import _TFL.Decorator

from   itertools                import chain as iter_chain

as_text = pyk.text_type

class M_Field (TFL.Meta.Object.__class__) :
    """Metaclass for field classes"""

# end class M_Field

@pyk.adapt__str__
class Base (TFL.Meta.BaM (TFL.Meta.Object, metaclass = M_Field)) :

    aq            = None
    attr_name     = None
    attr_names    = ()
    css_class_add = None

    html_sep      = "<br>"
    tag_set       = None
    tag_item      = None
    value_sep     = "; "

    def __init__ (self, resource, field_name, E_Type = None) :
        if self.attr_name is None :
            self.attr_name = field_name
        self.field_name    = field_name
        self.E_Type        = E_Type or resource.E_Type
        self.resource      = resource
    # end def __init__

    @Once_Property
    @getattr_safe
    def attr (self) :
        aq = self.aq
        if aq is not None and not is_undefined (aq) :
            return aq._attr
    # end def attr

    @Once_Property
    @getattr_safe
    def css_align (self) :
        if self.attr is not None :
            return getattr (self.attr, "css_align", None)
    # end def css_align

    @Once_Property
    @getattr_safe
    def css_class (self) :
        cc = self.css_classes
        return filtered_join  (" ", cc) if cc else ""
    # end def css_class

    @Once_Property
    @getattr_safe
    def css_classes (self) :
        result = []
        align  = self.css_align
        if align :
            result.append ("-".join (("align", align)))
        if self.css_class_add :
            result.append (self.css_class_add)
        return result
    # end def css_classes

    @property ### depends on currently selected language (I18N/L10N)
    @getattr_safe
    def description (self) :
        if self.attr is not None :
            return _T (self.attr.description)
    # end def description

    @Once_Property
    def fields (self) :
        result = self.resource._fields (self.attr_names, self.P_Type)
        return result
    # end def fields

    @Once_Property
    @getattr_safe
    def name (self) :
        if self.attr is not None :
            return self.aq._full_name
        else :
            return self.attr_name
    # end def name

    @Once_Property
    @getattr_safe
    def P_Type (self) :
        return self.E_Type if self.attr is None else self.attr.P_Type
    # end def P_Type

    @property
    def td_cols (self) :
        """Per default, a field has one column per row"""
        return (self, )
    # end def td_cols

    @property
    def th_cols (self) :
        """Per default, a field has one header column"""
        return (self, )
    # end def th_cols

    @property
    def th_cols0 (self) :
        """Per default, a field has no header column 0"""
        return (None, )
    # end def th_cols0

    @property ### depends on currently selected language (I18N/L10N)
    @getattr_safe
    def ui_name (self) :
        result = self.aq._ui_name_short_T if self.attr is not None \
            else _T (self.field_name)
        ### put `zero-width-space` before `/`
        return result.replace ("/", "\u200b/")
    # end def ui_name

    @Once_Property
    def _value_getter (self) :
        return getattr (Q, self.name)
    # end def _value_getter

    def as_html (self, o, renderer) :
        return self.value (o, renderer)
    # end def as_html

    def as_html_iter (self, o, renderer) :
        return (self.as_html (o, renderer), )
    # end def as_html_iter

    def css_class_dyn (self, obj, renderer) :
        return self.css_class
    # end def css_class_dyn

    def value (self, o, renderer) :
        result = None
        if isinstance (o, MOM.Id_Entity) :
            ### `FO` needs to do resolution of dotted names itself
            result = getattr (o.FO, self.name, None)
        if result is None :
            result = self._value_getter (o)
        return result
    # end def value

    def _set_as_html (self, values, renderer) :
        tag_set   = self.tag_set
        tag_item  = self.tag_item
        ti_head   = "<%s>"  % tag_item if tag_item else ""
        ti_tail   = "</%s>" % tag_item if tag_item else ""
        ts_head   = "<%s>"  % tag_set  if tag_set  else ""
        ts_tail   = "</%s>" % tag_set  if tag_set  else ""
        result    = self.html_sep.join \
            ("%s%s%s" % (ti_head, v or "&nbsp;", ti_tail) for v in values)
        result = "".join ([ts_head, result, ts_tail])
        return result
    # end def _set_as_html

    def _set_as_value (self, o, renderer) :
        return self.value_sep.join \
            (as_text (f.value (o, renderer)) for f in self.fields)
    # end def _set_as_value

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        if self.attr is not None :
            return getattr (self.attr, name)
        raise AttributeError (name)
    # end def __getattr__

    def __repr__ (self) :
        return str (self)
    # end def __repr__

    def __str__ (self) :
        return "<Field %s for %s>" % (self.ui_name, self.aq)
    # end def __str__

# end class Base

class AQ (Base) :
    """Field describing a queryable attribute accessible by `E_Type.AQ`."""

    def __init__ (self, * args, ** kw) :
        self.__super.__init__ (* args, ** kw)
        self.aq = getattr (self.E_Type.AQ, self.attr_name)
    # end def __init__

# end class AQ

class Attr_Set_1 (Base) :
    """Field describing a set of attributes displayed as a single column."""

    html_sep      = " "
    value_sep     = " "

    def value (self, o, renderer) :
        if self.aq :
            ### assume `attr_names` to be relative to `self.aq`
            o = self._value_getter (o)
        return self._set_as_value (o, renderer)
    # end def value

# end class Attr_Set_1

class Attr_Set_M (Base) :
    """Field describing a set of attributes displayed in multiple separate
       columns with a single header.
    """

    @Once_Property
    def fields (self) :
        result = self.__super.fields
        if len (result) > 1 :
            def fix (f, cssc) :
                f.css_class_add = filtered_join (" ", (f.css_class_add, cssc))
            fix (result [0], "col-set l")
            for f in result [1:-1] :
                fix (f, "col-set m")
            fix (result [-1], "col-set r")
        return result
    # end def fields

    @property
    def td_cols (self) :
        return tuple (iter_chain (* (f.td_cols for f in self.fields)))
    # end def td_cols

# end class Attr_Set_M

class Attr_Set_R (Attr_Set_1) :
    """Field describing a set of attributes displayed as separate
       lines/paragraphs/list-items in a single column.
    """

    html_sep      = ""
    tag_item      = "p"
    value_sep     = "; "

    def as_html (self, o, renderer) :
        return self._set_as_html (self.as_html_iter (o, renderer), renderer)
    # end def as_html

    def as_html_iter (self, o, renderer) :
        if self.aq :
            ### assume `attr_names` to be relative to `self.aq`
            o = self._value_getter (o)
        return iter_chain \
            (* tuple (f.as_html_iter (o, renderer) for f in self.fields))
    # end def as_html_iter

# end class Attr_Set_R

class Created (AQ) :
    """Field providing the creation date (without time) of an entity."""

    attr_name         = "creation_date"

    @property ### depends on currently selected language (I18N/L10N)
    @getattr_safe
    def description (self) :
        return _T ("Date of creation.")
    # end def description

    @property ### depends on currently selected language (I18N/L10N)
    @getattr_safe
    def ui_name (self) :
        return _T ("Created")
    # end def ui_name

    def as_html (self, o, renderer) :
        result = self.__super.as_html (o, renderer)
        result = result.replace ("-", zero_width_space + "-")
        return result
    # end def as_html

    def value (self, o, renderer) :
        return self.__super.value (o, renderer).split (" ") [0]
    # end def value

# end class Created

class Index (Base) :
    """Field providing the relative index of the object on the page."""

    css_class_add = "Index"

    @Once_Property
    def ui_name (self) :
        return "#"
    # end def ui_name

    def value (self, o, renderer) :
        return renderer.index
    # end def value

# end class Index

class _Id_Entity_Collection_ (AQ) :
    """Field for an attribute that refers to a collection of Id_Entities."""

    def __init__ (self, * args, ** kw) :
        self.__super.__init__ (* args, ** kw)
        if len (self.attr_names) > 1 :
            raise NotImplementedError \
                ( "%s %s doesn't support multiple nested attributes %s; "
                  "please wrap them"
                % (self.__class__.__name__, self, self.attr_names)
                )
    # end def __init__

    def as_html (self, o, renderer) :
        return self._set_as_html (self.as_html_iter (o, renderer), renderer)
    # end def as_html

    def as_html_iter (self, o, renderer) :
        fields = self.fields
        values = self._get_value (o)
        if fields :
            f = fields [0]
            return iter_chain \
                (* tuple (f.as_html_iter (v, renderer) for v in values))
        else :
            return (as_text (v.FO) for v in values)
    # end def as_html_iter

    def value (self, o, renderer) :
        fields = self.fields
        values = self._get_value (o)
        if fields :
            result = self._set_as_value (o, renderer)
        else :
            result = self.value_sep.join (as_text (r.FO) for r in values)
        return result
    # end def value

    def _get_value (self, o) :
        return self._value_getter (o)
    # end def _get_value

# end class _Id_Entity_Collection_

class Id_Entity_Collection_Size (AQ) :
    """Field providing the size of a collection of Id_Entities."""

    css_align         = "right"
    css_class_add     = "number"
    ui_name           = "#"

    @property ### depends on currently selected language (I18N/L10N)
    @getattr_safe
    def description (self) :
        return _T (self._description) % \
            (self.attr.P_Type.ui_name_T, self.E_Type.ui_name_T)
    # end def description

    @Once_Property
    @getattr_safe
    def _description (self) :
        return _ ("Number of %s belonging to %s")
    # end def _description

    def value (self, o, renderer) :
        return len (self._value_getter (o) or ())
    # end def value

# end class Id_Entity_Collection_Size

@TFL.Add_To_Class ("_gtw_field_type", MOM.Attr._A_Id_Entity_List_)
class Id_Entity_List (_Id_Entity_Collection_) :
    """Field for an attribute that refers to a [ordered] list of Id_Entities."""

# end class Id_Entity_List

@TFL.Add_To_Class ("_gtw_field_type", MOM.Attr._A_Id_Entity_Set_)
class Id_Entity_Set (_Id_Entity_Collection_) :
    """Field for an attribute that refers to a [unordered] set of Id_Entities."""

    @Once_Property
    @getattr_safe
    def sort_key (self) :
        return self.attr.P_Type.sorted_by
    # end def sort_key

    def _get_value (self, o) :
        return sorted (self.__super._get_value (o), key = self.sort_key)
    # end def _get_value

# end class Id_Entity_Set

class M_HTML_Link (AQ.__class__) :
    """Metaclass for `HTML_Link`"""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        if name != "HTML_Link" and not name.endswith ("_Set") :
            cls.Set = cls.__class__ \
                ( "_".join ((name, "Set"))
                , (cls, HTML_Link_Set)
                , dict (__module__ = cls.__module__)
                )
    # end def __init__

# end class M_HTML_Link

class HTML_Link (TFL.Meta.BaM (AQ, metaclass = M_HTML_Link)) :
    """Field that is displayed as HTML link"""

    protocol = None

    @Once_Property
    @getattr_safe
    def css_classes (self) :
        return self.__super.css_classes + ["link"]
    # end def css_classes

    @Once_Property
    @getattr_safe
    def title (self) :
        return None
    # end def title

    def as_html (self, o, renderer) :
        href      = self._as_html_href  (o, renderer)
        value     = self._as_html_value (o, renderer)
        title     = self._as_html_title (o, href, value)
        proto     = self.protocol
        fmt_head  = "<a"
        fmt_href  = "".join \
            ( ( " href=\""
              , "%(proto)s:" if proto and ":" not in href else ""
              , "%(href)s\""
              )
            ) if href else ""
        fmt_tail  = ">%(value)s</a>"
        fmt_title = " title=\"%(title)s\"" if title else ""
        fmt       = "".join ((fmt_head, fmt_href, fmt_title, fmt_tail))
        return fmt % vars ()
    # end def as_html

    def _as_html_href (self, o, renderer) :
        return self._as_html_value (o, renderer)
    # end def _as_html_href

    def _as_html_title (self, o, href, value) :
        return self.title
    # end def _as_html_title

    def _as_html_value (self, o, renderer) :
        return as_text (self.value (o, renderer).FO)
    # end def _as_html_value

# end class HTML_Link

class HTML_Link_Set (HTML_Link) :
    """Field comprising a set of `HTML_Link` values."""

    max_links = 0

    def as_html (self, o, renderer) :
        def _gen (self, o, renderer) :
            o_set   = self._value_getter (o)
            as_html = self.__super.as_html
            for elem in o_set :
                oo  = TFL.Record ()
                setattr (oo, self.name, elem)
                vv  = self._as_html_value (oo, renderer)
                yield vv, as_html (oo, renderer)
        links = sorted (_gen (self, o, renderer))
        max_l = self.max_links
        if max_l and max_l > 0 :
            links = links [:max_l]
        return "<br>".join (html for vv, html in links)
    # end def as_html

# end class HTML_Link_Set

class Account (HTML_Link) :
    """Field showing the person an `Account` instance."""

    protocol = "mailto"

    def _as_html_href (self, o, renderer) :
        account = self._value_getter (o)
        return account.name
    # end def _as_html_href

    def _as_html_title (self, o, href, value) :
        return "%s %s" % (_T ("Email"), value)
    # end def _as_html_title

    def _as_html_value (self, o, renderer) :
        account = self._value_getter (o)
        return account.FO.person if account.person else account.name
    # end def _as_html_value

# end class Account

class Account_Name (HTML_Link) :
    """Field showing the name of an `Account` instance."""

    protocol = "mailto"

    def _as_html_title (self, o, href, value) :
        return "%s %s" % (_T ("Email"), value)
    # end def _as_html_title

    def _as_html_value (self, o, renderer) :
        account = self._value_getter (o)
        return account.name
    # end def _as_html_value

# end class Account_Name

class Email (HTML_Link) :
    """Field showing an `Email` instance."""

    protocol = "mailto"

    def _as_html_title (self, o, href, value) :
        return _T ("Send email to %s") % (value, )
    # end def _as_html_title

# end class Email

class Phone (HTML_Link) :
    """Field showing a `Phone` instance."""

    protocol = "tel"

    def _as_html_href (self, o, renderer) :
        phone = self._value_getter (o)
        return "+%s %s %s" % tuple (phone.epk_raw [:-1])
    # end def _as_html_href

    def _as_html_title (self, o, href, value) :
        return _T ("Make phone call to %s") % (value, )
    # end def _as_html_title

# end class Phone

if __name__ != "__main__" :
    GTW.RST.TOP.MOM._Export_Module ()
### __END__ GTW.RST.TOP.MOM.Field
