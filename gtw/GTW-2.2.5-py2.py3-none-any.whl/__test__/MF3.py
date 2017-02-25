# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.__test__.MF3
#
# Purpose
#    Test GTW.MF3
#
# Revision Dates
#    25-Apr-2014 (CT) Creation
#    13-Jun-2014 (RS) Fix tests for `PAP.Group`
#    25-Aug-2014 (CT) Adapt to changes of `GTW.MF3.Completer`
#    27-Aug-2014 (CT) Add test `skip`
#    30-Mar-2015 (CT) Add test `single_primary`
#    29-Jul-2015 (CT) Adapt to name change of PAP.Phone attributes
#    22-Dec-2015 (CT) Add test `max_rev_ref`
#    22-Apr-2016 (CT) Adapt to change of `Date_Interval.start.completer`
#    26-Apr-2016 (CT) Adapt to `buddies` in `as_json_cargo`
#    17-Oct-2016 (CT) Add test `cls_structure`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                       import GTW
from   _MOM.import_MOM            import Q

import _GTW._OMP._PAP.import_PAP
GTW.OMP.PAP.Phone.change_attribute_default ("cc", "+43")

from   _GTW.__test__.model        import *
from   _GTW._MF3                  import Element as MF3_E

from   _TFL._Meta.Def_Map         import Def_Map as DM
from   _TFL._Meta.Single_Dispatch import Single_Dispatch
from   _TFL.Regexp                import Multi_Re_Replacer, Re_Replacer, re

import _GTW._OMP._SRM.Ranking

from   collections                import defaultdict

_cleaner = Re_Replacer \
    ( r"'\$sid' : '[0-9a-f]+'"
    , r"'$sid' : <sid value>"
    )

def show_elements (f, attr) :
    getter = getattr (Q, attr)
    for e in f.elements_transitive () :
        try :
            v = getter (e)
        except AttributeError :
            v = "---"
        if isinstance (v, TFL.Undef) :
            v = "---"
        print (("%s %s" % (e, v)).strip ())
# end def show_elements

@Single_Dispatch (T = MF3_E._Base_)
def elem_x (x, getters, default = "---") :
    nick   = "_".join \
        (p [0] for p in x.__class__.__name__.strip ("_").split ("_"))
    result = ["%-2s   " % (nick, )]
    for getter in getters :
        try :
            tail  = getter (x)
        except AttributeError :
            tail = default
        if isinstance (tail, TFL.Undef) :
            tail = default
        if isinstance (tail, dict) :
            tail = ", ".join \
                ("%s = %s" % (k, v) for k, v in sorted (pyk.iteritems (tail)))
        if isinstance (tail, (dict, list, tuple)) :
            tail = portable_repr (tail)
        result.append (str (tail))
    return result
# end def elem_x

def show_elements_x (f, * attrs, ** kw) :
    def _format (lens, elems) :
        return "  ".join \
            (("%-*s" % (l, e)) for l, e in zip (lens, elems)).rstrip ()
    default = kw.get ("---")
    filter  = kw.get ("filter", lambda x : True)
    getters = tuple (getattr (Q, attr) for attr in attrs)
    elems   = tuple \
        (   elem_x (e, getters, default = default)
        for e in f.elements_transitive () if filter (e)
        )
    lens    = list ((max (len (e) for e in es)) for es in zip (* elems))
    print (_format (lens, ("Type", ) + attrs))
    print ("=" * (sum (lens) + 2 * len (lens)))
    for es in elems :
        print (_format (lens, es))
# end def show_elements_x

def show_completers (f, * attrs, ** kw) :
    kw.setdefault ("filter", Q.completer != None)
    return show_elements_x (f, * attrs, ** kw)
# end def show_completers

def show_completers_js (f) :
    show_formatted (f.as_json_cargo ["completers"])
# end def show_completers_js

def show_field_values (f) :
    show_formatted (f.as_json_cargo ["cargo"] ["field_values"])
# end def show_field_values

def show_formatted (x) :
    result = _cleaner (formatted (x))
    print (result)
# end def show_formatted

def show_ui_allow (f) :
    fmt = "%-40s %5s %5s %5s"
    for e in f.field_elements :
        if e.action_buttons :
            print \
                  ( fmt
                  % (e, e.ui_allow_change, e.ui_allow_move, e.ui_allow_new)
                  )
# end def show_ui_allow

_test_cls_structure = r"""

    >>> mf3_classes = sorted \
    ...     ( (n, x) for n, x in MF3_E.__dict__.items ()
    ...     if isinstance (x, MF3_E._M_Element_)
    ...     )
    >>> for name, cls in mf3_classes :
    ...     print ("%%-25s : %%s" %% (name, ", ".join (x.__name__ for x in cls.__mro__[1:-3])))
    Entity                    : _Entity_, _Entity_Mixin_, _Element_, _Base_
    Entity_Rev_Ref            : _Field_Entity_Mixin_, _Entity_, _Entity_Mixin_, _Element_, _Base_
    Field                     : _Field_, _Field_Base_, _Element_, _Base_
    Field_Composite           : _Field_Composite_, _Field_Composite_Mixin_, _Field_, _Field_Base_, _Element_, _Base_
    Field_Entity              : _Field_Composite_Mixin_, _Field_Entity_Mixin_, _Entity_Mixin_, _Field_, _Field_Base_, _Element_, _Base_
    Field_Ref_Hidden          : Field_Entity, _Field_Composite_Mixin_, _Field_Entity_Mixin_, _Entity_Mixin_, _Field_, _Field_Base_, _Element_, _Base_
    Field_Rev_Ref             : _Field_Base_, _Element_, _Base_
    Field_Structured          : _Field_Composite_, _Field_Composite_Mixin_, _Field_, _Field_Base_, _Element_, _Base_
    _Element_                 : _Base_
    _Entity_                  : _Entity_Mixin_, _Element_, _Base_
    _Field_                   : _Field_Base_, _Element_, _Base_
    _Field_Base_              : _Element_, _Base_
    _Field_Composite_         : _Field_Composite_Mixin_, _Field_, _Field_Base_, _Element_, _Base_
    _Field_Composite_Mixin_   : _Element_, _Base_

    >>> f_map = defaultdict (set)
    >>> for f in ("_submit", "submitted_value") :
    ...   for name, cls in mf3_classes :
    ...     fl = list (x.__name__ for x in DM [(cls, f)])
    ...     f_map [f].update (fl)
    ...     print ("%%-25s : %%s : %%s" %% (name, f, ", ".join (fl) or "---"))
    Entity                    : _submit : _Entity_Mixin_
    Entity_Rev_Ref            : _submit : _Entity_Mixin_
    Field                     : _submit : Field
    Field_Composite           : _submit : _Field_Composite_
    Field_Entity              : _submit : _Entity_Mixin_, Field_Entity
    Field_Ref_Hidden          : _submit : _Entity_Mixin_, Field_Entity, Field_Ref_Hidden
    Field_Rev_Ref             : _submit : Field_Rev_Ref
    Field_Structured          : _submit : _Field_Composite_
    _Element_                 : _submit : ---
    _Entity_                  : _submit : _Entity_Mixin_
    _Field_                   : _submit : ---
    _Field_Base_              : _submit : ---
    _Field_Composite_         : _submit : _Field_Composite_
    _Field_Composite_Mixin_   : _submit : ---
    Entity                    : submitted_value : _Base_, _Entity_Mixin_
    Entity_Rev_Ref            : submitted_value : _Base_, _Entity_Mixin_
    Field                     : submitted_value : _Base_
    Field_Composite           : submitted_value : _Base_, _Field_Composite_Mixin_
    Field_Entity              : submitted_value : _Base_, _Entity_Mixin_, _Field_Composite_Mixin_, Field_Entity
    Field_Ref_Hidden          : submitted_value : _Base_, _Entity_Mixin_, _Field_Composite_Mixin_, Field_Entity, Field_Ref_Hidden
    Field_Rev_Ref             : submitted_value : _Base_
    Field_Structured          : submitted_value : _Base_, _Field_Composite_Mixin_
    _Element_                 : submitted_value : _Base_
    _Entity_                  : submitted_value : _Base_, _Entity_Mixin_
    _Field_                   : submitted_value : _Base_
    _Field_Base_              : submitted_value : _Base_
    _Field_Composite_         : submitted_value : _Base_, _Field_Composite_Mixin_
    _Field_Composite_Mixin_   : submitted_value : _Base_, _Field_Composite_Mixin_

    >>> for f, fl in sorted (f_map.items ()) :
    ...     print ("%%-25s : %%s" %% (f, ", ".join (sorted (fl, key = lambda x : (not x.startswith ("_"), x)))))
    _submit                   : _Entity_Mixin_, _Field_Composite_, Field, Field_Entity, Field_Ref_Hidden, Field_Rev_Ref
    submitted_value           : _Base_, _Entity_Mixin_, _Field_Composite_Mixin_, Field_Entity, Field_Ref_Hidden

"""

_test_element = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> scope.db_meta_data.dbid = '2d802327-5c99-49ca-9af7-2ddc6b4c648b'

    >>> PAP = scope.PAP
    >>> p   = PAP.Person ("Tanzer", "Christian", lifetime = ("19590926", ), raw=True)
    >>> ph  = PAP.Phone  ("43", "1", "98765432", raw=True)
    >>> pph = PAP.Person_has_Phone (p, ph, desc = "example", extension = "42", raw=True)

    >>> p_attr_spec= { "lifetime.start" : dict (init = "2000-07-23"), "sex" : dict (init = "M")}
    >>> F_Person   = MF3_E.Entity.Auto (scope.PAP.Person, id_prefix = "X")
    >>> F_Person_s = MF3_E.Entity.Auto (scope.PAP.Person, id_prefix = "Y", attr_spec = { "lifetime.finish" : dict (skip = True)})
    >>> F_Person_z = MF3_E.Entity.Auto (scope.PAP.Person, id_prefix = "Z", include_rev_refs = ("phones", ))
    >>> f_Person   = F_Person (scope)
    >>> f_Person_s = F_Person_s (scope, attr_spec = p_attr_spec)
    >>> f_Person_z = F_Person_z (scope)
    >>> f_p        = F_Person (scope, p)
    >>> f_p_s      = F_Person_s (scope, p, attr_spec = p_attr_spec)
    >>> f_p_z      = F_Person_z (scope, p)
    >>> f_p_z2     = F_Person_z (scope, p)
    >>> _          = f_p_z2 ["Z-26:phones"].add ()
    >>> _          = f_p_z2 ["Z-26:phones"].add ()

    >>> F_Person
    <class Entity X-26>

    >>> F_Person ["X-26:lifetime.start"]
    <class Field X-26:lifetime.start>

    >>> F_Person ["lifetime.finish"]
    <class Field X-26:lifetime.finish>

    >>> f_Person ["X-26:lifetime.start"]
    <Field X-26:lifetime.start>

    >>> f_Person ["lifetime.finish"]
    <Field X-26:lifetime.finish>

    >>> show_elements (f_Person, "cooked")
    <Entity X-26> ---
    <Field X-26:last_name>
    <Field X-26:first_name>
    <Field X-26:middle_name>
    <Field X-26:title>
    <Field_Composite X-26:lifetime> ()
    <Field X-26:lifetime.start> None
    <Field X-26:lifetime.finish> None
    <Field X-26:sex> None

    >>> show_elements (f_p, "cooked")
    <Entity X-26> ---
    <Field X-26:last_name> tanzer
    <Field X-26:first_name> christian
    <Field X-26:middle_name>
    <Field X-26:title>
    <Field_Composite X-26:lifetime> ('1959-09-26', )
    <Field X-26:lifetime.start> 1959-09-26
    <Field X-26:lifetime.finish> None
    <Field X-26:sex> None

    >>> show_elements (f_p, "q_name")
    <Entity X-26> None
    <Field X-26:last_name> last_name
    <Field X-26:first_name> first_name
    <Field X-26:middle_name> middle_name
    <Field X-26:title> title
    <Field_Composite X-26:lifetime> lifetime
    <Field X-26:lifetime.start> lifetime.start
    <Field X-26:lifetime.finish> lifetime.finish
    <Field X-26:sex> sex

    >>> for e in f_p.field_elements :
    ...     print (e)
    <Field X-26:last_name>
    <Field X-26:first_name>
    <Field X-26:middle_name>
    <Field X-26:title>
    <Field X-26:lifetime.start>
    <Field X-26:lifetime.finish>
    <Field X-26:sex>

    >>> show_elements (f_Person, "edit")
    <Entity X-26> ---
    <Field X-26:last_name>
    <Field X-26:first_name>
    <Field X-26:middle_name>
    <Field X-26:title>
    <Field_Composite X-26:lifetime>
    <Field X-26:lifetime.start>
    <Field X-26:lifetime.finish>
    <Field X-26:sex>

    >>> show_elements (f_Person_s, "edit")
    <Entity Y-26> ---
    <Field Y-26:last_name>
    <Field Y-26:first_name>
    <Field Y-26:middle_name>
    <Field Y-26:title>
    <Field_Composite Y-26:lifetime>
    <Field Y-26:lifetime.start> 2000-07-23
    <Field Y-26:sex> M

    >>> show_elements (f_p, "edit")
    <Entity X-26> ---
    <Field X-26:last_name> Tanzer
    <Field X-26:first_name> Christian
    <Field X-26:middle_name>
    <Field X-26:title>
    <Field_Composite X-26:lifetime>
    <Field X-26:lifetime.start> 1959-09-26
    <Field X-26:lifetime.finish>
    <Field X-26:sex>

    >>> show_elements (f_p_s, "edit")
    <Entity Y-26> ---
    <Field Y-26:last_name> Tanzer
    <Field Y-26:first_name> Christian
    <Field Y-26:middle_name>
    <Field Y-26:title>
    <Field_Composite Y-26:lifetime>
    <Field Y-26:lifetime.start> 2000-07-23
    <Field Y-26:sex> M

    >>> show_elements (f_p, "ui_display")
    <Entity X-26> Tanzer Christian
    <Field X-26:last_name> Tanzer
    <Field X-26:first_name> Christian
    <Field X-26:middle_name>
    <Field X-26:title>
    <Field_Composite X-26:lifetime> 1959-09-26
    <Field X-26:lifetime.start> 1959-09-26
    <Field X-26:lifetime.finish>
    <Field X-26:sex>

    >>> show_elements (f_p, "essence")
    <Entity X-26> ('tanzer', 'christian', '', '')
    <Field X-26:last_name> ('tanzer', 'christian', '', '')
    <Field X-26:first_name> ('tanzer', 'christian', '', '')
    <Field X-26:middle_name> ('tanzer', 'christian', '', '')
    <Field X-26:title> ('tanzer', 'christian', '', '')
    <Field_Composite X-26:lifetime> ('1959-09-26', )
    <Field X-26:lifetime.start> ('1959-09-26', )
    <Field X-26:lifetime.finish> ('1959-09-26', )
    <Field X-26:sex> ('tanzer', 'christian', '', '')

    >>> show_elements (f_p, "Entity.essence")
    <Entity X-26> ('tanzer', 'christian', '', '')
    <Field X-26:last_name> ('tanzer', 'christian', '', '')
    <Field X-26:first_name> ('tanzer', 'christian', '', '')
    <Field X-26:middle_name> ('tanzer', 'christian', '', '')
    <Field X-26:title> ('tanzer', 'christian', '', '')
    <Field_Composite X-26:lifetime> ('tanzer', 'christian', '', '')
    <Field X-26:lifetime.start> ('tanzer', 'christian', '', '')
    <Field X-26:lifetime.finish> ('tanzer', 'christian', '', '')
    <Field X-26:sex> ('tanzer', 'christian', '', '')

    >>> show_elements (f_Person, "root")
    <Entity X-26> <Entity X-26>
    <Field X-26:last_name> <Entity X-26>
    <Field X-26:first_name> <Entity X-26>
    <Field X-26:middle_name> <Entity X-26>
    <Field X-26:title> <Entity X-26>
    <Field_Composite X-26:lifetime> <Entity X-26>
    <Field X-26:lifetime.start> <Entity X-26>
    <Field X-26:lifetime.finish> <Entity X-26>
    <Field X-26:sex> <Entity X-26>

    >>> show_elements (f_Person, "Entity")
    <Entity X-26> <Entity X-26>
    <Field X-26:last_name> <Entity X-26>
    <Field X-26:first_name> <Entity X-26>
    <Field X-26:middle_name> <Entity X-26>
    <Field X-26:title> <Entity X-26>
    <Field_Composite X-26:lifetime> <Entity X-26>
    <Field X-26:lifetime.start> <Entity X-26>
    <Field X-26:lifetime.finish> <Entity X-26>
    <Field X-26:sex> <Entity X-26>

    >>> show_elements (f_Person_z, "Entity")
    <Entity Z-26> <Entity Z-26>
    <Field Z-26:last_name> <Entity Z-26>
    <Field Z-26:first_name> <Entity Z-26>
    <Field Z-26:middle_name> <Entity Z-26>
    <Field Z-26:title> <Entity Z-26>
    <Field_Composite Z-26:lifetime> <Entity Z-26>
    <Field Z-26:lifetime.start> <Entity Z-26>
    <Field Z-26:lifetime.finish> <Entity Z-26>
    <Field Z-26:sex> <Entity Z-26>
    <Field_Rev_Ref Z-26:phones> <Entity Z-26>

    >>> show_elements (f_Person, "template_macro")
    <Entity X-26> Entity_Form
    <Field X-26:last_name> Field
    <Field X-26:first_name> Field
    <Field X-26:middle_name> Field
    <Field X-26:title> Field
    <Field_Composite X-26:lifetime> Field_Composite
    <Field X-26:lifetime.start> Field
    <Field X-26:lifetime.finish> Field
    <Field X-26:sex> Field

    >>> show_elements (f_Person, "template_module")
    <Entity X-26> mf3
    <Field X-26:last_name> None
    <Field X-26:first_name> None
    <Field X-26:middle_name> None
    <Field X-26:title> None
    <Field_Composite X-26:lifetime> mf3_h_cols
    <Field X-26:lifetime.start> None
    <Field X-26:lifetime.finish> None
    <Field X-26:sex> None

    >>> show_elements (f_Person_z ["phones"].proto, "parent")
    <class Entity_Rev_Ref Z-26:phones> <class Field_Rev_Ref Z-26:phones>
    <class Field_Entity Z-26:phones::right> <class Entity_Rev_Ref Z-26:phones>
    <class Field Z-26:phones::right.cc> <class Field_Entity Z-26:phones::right>
    <class Field Z-26:phones::right.ndc> <class Field_Entity Z-26:phones::right>
    <class Field Z-26:phones::right.sn> <class Field_Entity Z-26:phones::right>
    <class Field Z-26:phones::extension> <class Entity_Rev_Ref Z-26:phones>
    <class Field Z-26:phones::desc> <class Entity_Rev_Ref Z-26:phones>
    <class Field_Ref_Hidden Z-26:phones::left> <class Entity_Rev_Ref Z-26:phones>
    <class Field Z-26:phones::left.last_name> <class Field_Ref_Hidden Z-26:phones::left>
    <class Field Z-26:phones::left.first_name> <class Field_Ref_Hidden Z-26:phones::left>
    <class Field Z-26:phones::left.middle_name> <class Field_Ref_Hidden Z-26:phones::left>
    <class Field Z-26:phones::left.title> <class Field_Ref_Hidden Z-26:phones::left>

    >>> show_elements (f_p_z, "Entity")
    <Entity Z-26> <Entity Z-26>
    <Field Z-26:last_name> <Entity Z-26>
    <Field Z-26:first_name> <Entity Z-26>
    <Field Z-26:middle_name> <Entity Z-26>
    <Field Z-26:title> <Entity Z-26>
    <Field_Composite Z-26:lifetime> <Entity Z-26>
    <Field Z-26:lifetime.start> <Entity Z-26>
    <Field Z-26:lifetime.finish> <Entity Z-26>
    <Field Z-26:sex> <Entity Z-26>
    <Field_Rev_Ref Z-26:phones> <Entity Z-26>
    <Entity_Rev_Ref Z-26:phones@3> <Entity_Rev_Ref Z-26:phones@3>
    <Field_Entity Z-26:phones::right@3> <Entity_Rev_Ref Z-26:phones@3>
    <Field Z-26:phones::right.cc@3> <Field_Entity Z-26:phones::right@3>
    <Field Z-26:phones::right.ndc@3> <Field_Entity Z-26:phones::right@3>
    <Field Z-26:phones::right.sn@3> <Field_Entity Z-26:phones::right@3>
    <Field Z-26:phones::extension@3> <Entity_Rev_Ref Z-26:phones@3>
    <Field Z-26:phones::desc@3> <Entity_Rev_Ref Z-26:phones@3>
    <Field_Ref_Hidden Z-26:phones::left@3> <Entity_Rev_Ref Z-26:phones@3>

    >>> show_elements (f_p_z, "essence")
    <Entity Z-26> ('tanzer', 'christian', '', '')
    <Field Z-26:last_name> ('tanzer', 'christian', '', '')
    <Field Z-26:first_name> ('tanzer', 'christian', '', '')
    <Field Z-26:middle_name> ('tanzer', 'christian', '', '')
    <Field Z-26:title> ('tanzer', 'christian', '', '')
    <Field_Composite Z-26:lifetime> ('1959-09-26', )
    <Field Z-26:lifetime.start> ('1959-09-26', )
    <Field Z-26:lifetime.finish> ('1959-09-26', )
    <Field Z-26:sex> ('tanzer', 'christian', '', '')
    <Field_Rev_Ref Z-26:phones> ('tanzer', 'christian', '', '')
    <Entity_Rev_Ref Z-26:phones@3> (('tanzer', 'christian', '', ''), ('43', '1', '98765432'), '42')
    <Field_Entity Z-26:phones::right@3> ('43', '1', '98765432')
    <Field Z-26:phones::right.cc@3> ('43', '1', '98765432')
    <Field Z-26:phones::right.ndc@3> ('43', '1', '98765432')
    <Field Z-26:phones::right.sn@3> ('43', '1', '98765432')
    <Field Z-26:phones::extension@3> (('tanzer', 'christian', '', ''), ('43', '1', '98765432'), '42')
    <Field Z-26:phones::desc@3> (('tanzer', 'christian', '', ''), ('43', '1', '98765432'), '42')
    <Field_Ref_Hidden Z-26:phones::left@3> ('tanzer', 'christian', '', '')

    >>> show_elements (f_p_z, "label")
    <Entity Z-26> Person
    <Field Z-26:last_name> Last name
    <Field Z-26:first_name> First name
    <Field Z-26:middle_name> Middle name
    <Field Z-26:title> Academic title
    <Field_Composite Z-26:lifetime> Lifetime
    <Field Z-26:lifetime.start> Start
    <Field Z-26:lifetime.finish> Finish
    <Field Z-26:sex> Sex
    <Field_Rev_Ref Z-26:phones> Phones
    <Entity_Rev_Ref Z-26:phones@3> Person has Phone
    <Field_Entity Z-26:phones::right@3> Phone
    <Field Z-26:phones::right.cc@3> Country code
    <Field Z-26:phones::right.ndc@3> Network destination code
    <Field Z-26:phones::right.sn@3> Subscriber number
    <Field Z-26:phones::extension@3> Extension
    <Field Z-26:phones::desc@3> Description
    <Field_Ref_Hidden Z-26:phones::left@3> Person

    >>> show_elements (f_p_z, "_po_index")
    <Entity Z-26> None
    <Field Z-26:last_name> None
    <Field Z-26:first_name> None
    <Field Z-26:middle_name> None
    <Field Z-26:title> None
    <Field_Composite Z-26:lifetime> None
    <Field Z-26:lifetime.start> None
    <Field Z-26:lifetime.finish> None
    <Field Z-26:sex> None
    <Field_Rev_Ref Z-26:phones> None
    <Entity_Rev_Ref Z-26:phones@3> None
    <Field_Entity Z-26:phones::right@3> None
    <Field Z-26:phones::right.cc@3> None
    <Field Z-26:phones::right.ndc@3> None
    <Field Z-26:phones::right.sn@3> None
    <Field Z-26:phones::extension@3> None
    <Field Z-26:phones::desc@3> None
    <Field_Ref_Hidden Z-26:phones::left@3> None

    >>> show_elements (f_p_z, "po_index")
    <Entity Z-26> 0
    <Field Z-26:last_name> 1
    <Field Z-26:first_name> 2
    <Field Z-26:middle_name> 3
    <Field Z-26:title> 4
    <Field_Composite Z-26:lifetime> 5
    <Field Z-26:lifetime.start> 6
    <Field Z-26:lifetime.finish> 7
    <Field Z-26:sex> 8
    <Field_Rev_Ref Z-26:phones> 9
    <Entity_Rev_Ref Z-26:phones@3> 10
    <Field_Entity Z-26:phones::right@3> 11
    <Field Z-26:phones::right.cc@3> 12
    <Field Z-26:phones::right.ndc@3> 13
    <Field Z-26:phones::right.sn@3> 14
    <Field Z-26:phones::extension@3> 15
    <Field Z-26:phones::desc@3> 16
    <Field_Ref_Hidden Z-26:phones::left@3> 17

    >>> show_elements (f_p_z, "_po_index")
    <Entity Z-26> 0
    <Field Z-26:last_name> 1
    <Field Z-26:first_name> 2
    <Field Z-26:middle_name> 3
    <Field Z-26:title> 4
    <Field_Composite Z-26:lifetime> 5
    <Field Z-26:lifetime.start> 6
    <Field Z-26:lifetime.finish> 7
    <Field Z-26:sex> 8
    <Field_Rev_Ref Z-26:phones> 9
    <Entity_Rev_Ref Z-26:phones@3> 10
    <Field_Entity Z-26:phones::right@3> 11
    <Field Z-26:phones::right.cc@3> 12
    <Field Z-26:phones::right.ndc@3> 13
    <Field Z-26:phones::right.sn@3> 14
    <Field Z-26:phones::extension@3> 15
    <Field Z-26:phones::desc@3> 16
    <Field_Ref_Hidden Z-26:phones::left@3> 17

    >>> f_p_z.reset_once_properties ()

    >>> print (f_p_z, f_p_z._po_index)
    <Entity Z-26> None

    >>> f_p_z ["Z-26:phones"]
    <Field_Rev_Ref Z-26:phones>

    >>> f_p_z ["Z-26:phones@3"]
    <Entity_Rev_Ref Z-26:phones@3>

    >>> show_elements (f_p_z, "id")
    <Entity Z-26> Z-26
    <Field Z-26:last_name> Z-26:last_name
    <Field Z-26:first_name> Z-26:first_name
    <Field Z-26:middle_name> Z-26:middle_name
    <Field Z-26:title> Z-26:title
    <Field_Composite Z-26:lifetime> Z-26:lifetime
    <Field Z-26:lifetime.start> Z-26:lifetime.start
    <Field Z-26:lifetime.finish> Z-26:lifetime.finish
    <Field Z-26:sex> Z-26:sex
    <Field_Rev_Ref Z-26:phones> Z-26:phones
    <Entity_Rev_Ref Z-26:phones@3> Z-26:phones@3
    <Field_Entity Z-26:phones::right@3> Z-26:phones::right@3
    <Field Z-26:phones::right.cc@3> Z-26:phones::right.cc@3
    <Field Z-26:phones::right.ndc@3> Z-26:phones::right.ndc@3
    <Field Z-26:phones::right.sn@3> Z-26:phones::right.sn@3
    <Field Z-26:phones::extension@3> Z-26:phones::extension@3
    <Field Z-26:phones::desc@3> Z-26:phones::desc@3
    <Field_Ref_Hidden Z-26:phones::left@3> Z-26:phones::left@3

    >>> show_elements (f_p_z, "index")
    <Entity Z-26>
    <Field Z-26:last_name>
    <Field Z-26:first_name>
    <Field Z-26:middle_name>
    <Field Z-26:title>
    <Field_Composite Z-26:lifetime>
    <Field Z-26:lifetime.start>
    <Field Z-26:lifetime.finish>
    <Field Z-26:sex>
    <Field_Rev_Ref Z-26:phones>
    <Entity_Rev_Ref Z-26:phones@3> @3
    <Field_Entity Z-26:phones::right@3> @3
    <Field Z-26:phones::right.cc@3> @3
    <Field Z-26:phones::right.ndc@3> @3
    <Field Z-26:phones::right.sn@3> @3
    <Field Z-26:phones::extension@3> @3
    <Field Z-26:phones::desc@3> @3
    <Field_Ref_Hidden Z-26:phones::left@3> @3

    >>> show_elements (f_p_z, "parent")
    <Entity Z-26> None
    <Field Z-26:last_name> <Entity Z-26>
    <Field Z-26:first_name> <Entity Z-26>
    <Field Z-26:middle_name> <Entity Z-26>
    <Field Z-26:title> <Entity Z-26>
    <Field_Composite Z-26:lifetime> <Entity Z-26>
    <Field Z-26:lifetime.start> <Field_Composite Z-26:lifetime>
    <Field Z-26:lifetime.finish> <Field_Composite Z-26:lifetime>
    <Field Z-26:sex> <Entity Z-26>
    <Field_Rev_Ref Z-26:phones> <Entity Z-26>
    <Entity_Rev_Ref Z-26:phones@3> <Field_Rev_Ref Z-26:phones>
    <Field_Entity Z-26:phones::right@3> <Entity_Rev_Ref Z-26:phones@3>
    <Field Z-26:phones::right.cc@3> <Field_Entity Z-26:phones::right@3>
    <Field Z-26:phones::right.ndc@3> <Field_Entity Z-26:phones::right@3>
    <Field Z-26:phones::right.sn@3> <Field_Entity Z-26:phones::right@3>
    <Field Z-26:phones::extension@3> <Entity_Rev_Ref Z-26:phones@3>
    <Field Z-26:phones::desc@3> <Entity_Rev_Ref Z-26:phones@3>
    <Field_Ref_Hidden Z-26:phones::left@3> <Entity_Rev_Ref Z-26:phones@3>

    >>> show_elements (f_p_z, "q_name")
    <Entity Z-26> None
    <Field Z-26:last_name> last_name
    <Field Z-26:first_name> first_name
    <Field Z-26:middle_name> middle_name
    <Field Z-26:title> title
    <Field_Composite Z-26:lifetime> lifetime
    <Field Z-26:lifetime.start> lifetime.start
    <Field Z-26:lifetime.finish> lifetime.finish
    <Field Z-26:sex> sex
    <Field_Rev_Ref Z-26:phones> phones
    <Entity_Rev_Ref Z-26:phones@3> phones
    <Field_Entity Z-26:phones::right@3> phones.right
    <Field Z-26:phones::right.cc@3> phones.right.cc
    <Field Z-26:phones::right.ndc@3> phones.right.ndc
    <Field Z-26:phones::right.sn@3> phones.right.sn
    <Field Z-26:phones::extension@3> phones.extension
    <Field Z-26:phones::desc@3> phones.desc
    <Field_Ref_Hidden Z-26:phones::left@3> phones.left

    >>> show_elements (f_p_z, "r_name")
    <Entity Z-26> ---
    <Field Z-26:last_name> last_name
    <Field Z-26:first_name> first_name
    <Field Z-26:middle_name> middle_name
    <Field Z-26:title> title
    <Field_Composite Z-26:lifetime> lifetime
    <Field Z-26:lifetime.start> lifetime.start
    <Field Z-26:lifetime.finish> lifetime.finish
    <Field Z-26:sex> sex
    <Field_Rev_Ref Z-26:phones> phones
    <Entity_Rev_Ref Z-26:phones@3> ---
    <Field_Entity Z-26:phones::right@3> right
    <Field Z-26:phones::right.cc@3> cc
    <Field Z-26:phones::right.ndc@3> ndc
    <Field Z-26:phones::right.sn@3> sn
    <Field Z-26:phones::extension@3> extension
    <Field Z-26:phones::desc@3> desc
    <Field_Ref_Hidden Z-26:phones::left@3> left

    >>> for e in f_p.entity_elements :
    ...     print (e, portable_repr (sorted (getattr (e, "_Element_Map", []))))
    <Entity X-26> ['X-26:first_name', 'X-26:last_name', 'X-26:lifetime', 'X-26:lifetime.finish', 'X-26:lifetime.start', 'X-26:middle_name', 'X-26:sex', 'X-26:title', 'first_name', 'last_name', 'lifetime', 'lifetime.finish', 'lifetime.start', 'middle_name', 'sex', 'title']

    >>> for e in f_p_z.entity_elements :
    ...     print (e, portable_repr (sorted (getattr (e, "_Element_Map", []))))
    <Entity Z-26> ['Z-26:first_name', 'Z-26:last_name', 'Z-26:lifetime', 'Z-26:lifetime.finish', 'Z-26:lifetime.start', 'Z-26:middle_name', 'Z-26:phones', 'Z-26:phones::desc@3', 'Z-26:phones::extension@3', 'Z-26:phones::left.first_name@3', 'Z-26:phones::left.last_name@3', 'Z-26:phones::left.middle_name@3', 'Z-26:phones::left.title@3', 'Z-26:phones::left@3', 'Z-26:phones::right.cc@3', 'Z-26:phones::right.ndc@3', 'Z-26:phones::right.sn@3', 'Z-26:phones::right@3', 'Z-26:phones@3', 'Z-26:sex', 'Z-26:title', 'first_name', 'last_name', 'lifetime', 'lifetime.finish', 'lifetime.start', 'middle_name', 'phones', 'phones.desc', 'phones.extension', 'phones.left', 'phones.left.first_name', 'phones.left.last_name', 'phones.left.middle_name', 'phones.left.title', 'phones.right', 'phones.right.cc', 'phones.right.ndc', 'phones.right.sn', 'sex', 'title']
    <Entity_Rev_Ref Z-26:phones@3> ['Z-26:phones::desc@3', 'Z-26:phones::extension@3', 'Z-26:phones::left.first_name@3', 'Z-26:phones::left.last_name@3', 'Z-26:phones::left.middle_name@3', 'Z-26:phones::left.title@3', 'Z-26:phones::left@3', 'Z-26:phones::right.cc@3', 'Z-26:phones::right.ndc@3', 'Z-26:phones::right.sn@3', 'Z-26:phones::right@3', 'desc', 'extension', 'left', 'left.first_name', 'left.last_name', 'left.middle_name', 'left.title', 'phones.desc', 'phones.extension', 'phones.left', 'phones.left.first_name', 'phones.left.last_name', 'phones.left.middle_name', 'phones.left.title', 'phones.right', 'phones.right.cc', 'phones.right.ndc', 'phones.right.sn', 'right', 'right.cc', 'right.ndc', 'right.sn']
    <Field_Entity Z-26:phones::right@3> []

    >>> print (F_Person_z ["Z-26:phones"])
    <class Field_Rev_Ref Z-26:phones>

    >>> F_Person_z ["Z-26:phones::left.first_name"]
    <class Field Z-26:phones::left.first_name>

    >>> F_Person_z ["Z-26:phones"] ["Z-26:phones::left.first_name"]
    <class Field Z-26:phones::left.first_name>

    >>> F_Person_z ["Z-26:phones::extension"]
    <class Field Z-26:phones::extension>

    >>> F_Person_z ["Z-26:phones"] ["extension"]
    <class Field Z-26:phones::extension>

    >>> proto = f_p_z ["Z-26:phones"].proto

    >>> print (portable_repr (sorted (proto._Element_Map)))
    ['Z-26:phones::desc', 'Z-26:phones::extension', 'Z-26:phones::left', 'Z-26:phones::left.first_name', 'Z-26:phones::left.last_name', 'Z-26:phones::left.middle_name', 'Z-26:phones::left.title', 'Z-26:phones::right', 'Z-26:phones::right.cc', 'Z-26:phones::right.ndc', 'Z-26:phones::right.sn', 'desc', 'extension', 'left', 'left.first_name', 'left.last_name', 'left.middle_name', 'left.title', 'phones.desc', 'phones.extension', 'phones.left', 'phones.left.first_name', 'phones.left.last_name', 'phones.left.middle_name', 'phones.left.title', 'phones.right', 'phones.right.cc', 'phones.right.ndc', 'phones.right.sn', 'right', 'right.cc', 'right.ndc', 'right.sn']

    >>> print (proto, proto.__class__, list (proto.elements_transitive ()))
    <class Entity_Rev_Ref Z-26:phones> <class '_GTW._MF3.Element.M_Entity_Rev_Ref'> [<class Entity_Rev_Ref Z-26:phones>, <class Field_Entity Z-26:phones::right>, <class Field Z-26:phones::right.cc>, <class Field Z-26:phones::right.ndc>, <class Field Z-26:phones::right.sn>, <class Field Z-26:phones::extension>, <class Field Z-26:phones::desc>, <class Field_Ref_Hidden Z-26:phones::left>, <class Field Z-26:phones::left.last_name>, <class Field Z-26:phones::left.first_name>, <class Field Z-26:phones::left.middle_name>, <class Field Z-26:phones::left.title>]

    >>> print (f_p_z ["Z-26:phones"])
    <Field_Rev_Ref Z-26:phones>

    >>> print (f_p_z ["Z-26:phones::left.first_name@3"])
    <Field Z-26:phones::left.first_name@3>

    >>> print (f_p_z ["Z-26:phones::extension@3"])
    <Field Z-26:phones::extension@3>

    >>> show_completers (f_p, "q_name", "attr.completer.kind")
    Type   q_name           attr.completer.kind
    ==============================
    F      last_name        Atom
    F      first_name       Atom
    F      middle_name      Atom
    F      title            Atom
    F      lifetime.start   Atom
    F      lifetime.finish  Atom

    >>> show_completers (f_p_z, "q_name", "attr.completer.kind")
    Type   q_name            attr.completer.kind
    ===============================
    F      last_name         Atom
    F      first_name        Atom
    F      middle_name       Atom
    F      title             Atom
    F      lifetime.start    Atom
    F      lifetime.finish   Atom
    F      phones.right.cc   Atom
    F      phones.right.ndc  Atom
    F      phones.right.sn   Atom
    F      phones.desc       Atom

    >>> show_field_values (f_p)
    { 'X-26:first_name' : {'init' : 'Christian'}
    , 'X-26:last_name' : {'init' : 'Tanzer'}
    , 'X-26:lifetime.finish' : {}
    , 'X-26:lifetime.start' : {'init' : '1959-09-26'}
    , 'X-26:middle_name' : {}
    , 'X-26:sex' : {}
    , 'X-26:title' : {}
    }

    >>> show_field_values (f_p_z)
    { 'Z-26:first_name' : {'init' : 'Christian'}
    , 'Z-26:last_name' : {'init' : 'Tanzer'}
    , 'Z-26:lifetime.finish' : {}
    , 'Z-26:lifetime.start' : {'init' : '1959-09-26'}
    , 'Z-26:middle_name' : {}
    , 'Z-26:phones::desc@3' : {'init' : 'example'}
    , 'Z-26:phones::extension@3' : {'init' : '42'}
    , 'Z-26:phones::left@3' :
        { 'init' :
            { 'cid' : 1
            , 'display' : 'Tanzer Christian'
            , 'pid' : 1
            }
        }
    , 'Z-26:phones::right.cc@3' : {'init' : '+43'}
    , 'Z-26:phones::right.ndc@3' : {'init' : '1'}
    , 'Z-26:phones::right.sn@3' : {'init' : '98765432'}
    , 'Z-26:phones::right@3' :
        { 'init' :
            { 'cid' : 2
            , 'display' : '+43-1-987 654 32'
            , 'pid' : 2
            }
        }
    , 'Z-26:phones@3' :
        { 'init' :
            { 'cid' : 3
            , 'display' : 'Tanzer Christian, +43-1-987 654 32, 42'
            , 'pid' : 3
            }
        }
    , 'Z-26:sex' : {}
    , 'Z-26:title' : {}
    }

    >>> show_completers (f_p, "q_name", "completer.buddies_id", "polisher.id")
    Type   q_name           completer.buddies_id  polisher.id
    ==============================
    F      last_name        1  5
    F      first_name       1  6
    F      middle_name      1  7
    F      title            2  2
    F      lifetime.start   3  8
    F      lifetime.finish  4  8

    >>> print (formatted (f_p.as_json_cargo ["buddies"]))
    { 1 :
        [ 'X-26:first_name'
        , 'X-26:last_name'
        , 'X-26:middle_name'
        , 'X-26:title'
        ]
    , 2 : ['X-26:title']
    , 3 : ['X-26:lifetime.start']
    , 4 : ['X-26:lifetime.finish']
    , 5 : ['X-26:last_name']
    , 6 : ['X-26:first_name']
    , 7 : ['X-26:middle_name']
    , 8 :
        [ 'X-26:lifetime.finish'
        , 'X-26:lifetime.start'
        ]
    }

    >>> show_completers (f_p_z, "q_name", "completer.buddies_id", "polisher.id")
    Type   q_name            completer.buddies_id  polisher.id
    ==================================
    F      last_name         1  9
    F      first_name        1  10
    F      middle_name       1  11
    F      title             2  2
    F      lifetime.start    3  12
    F      lifetime.finish   4  12
    F      phones.right.cc   5  7
    F      phones.right.ndc  6  7
    F      phones.right.sn   7  7
    F      phones.desc       8  None

    >>> print (formatted (f_p_z.as_json_cargo ["buddies"]))
    { 1 :
        [ 'Z-26:first_name'
        , 'Z-26:last_name'
        , 'Z-26:middle_name'
        , 'Z-26:title'
        ]
    , 2 : ['Z-26:title']
    , 3 : ['Z-26:lifetime.start']
    , 4 : ['Z-26:lifetime.finish']
    , 5 : ['Z-26:phones::right.cc@3']
    , 6 :
        [ 'Z-26:phones::right.cc@3'
        , 'Z-26:phones::right.ndc@3'
        ]
    , 7 :
        [ 'Z-26:phones::right.cc@3'
        , 'Z-26:phones::right.ndc@3'
        , 'Z-26:phones::right.sn@3'
        ]
    , 8 : ['Z-26:phones::desc@3']
    , 9 : ['Z-26:last_name']
    , 10 : ['Z-26:first_name']
    , 11 : ['Z-26:middle_name']
    , 12 :
        [ 'Z-26:lifetime.finish'
        , 'Z-26:lifetime.start'
        ]
    }

    >>> print (portable_repr (sorted (f_p._Element_Map)))
    ['X-26:first_name', 'X-26:last_name', 'X-26:lifetime', 'X-26:lifetime.finish', 'X-26:lifetime.start', 'X-26:middle_name', 'X-26:sex', 'X-26:title', 'first_name', 'last_name', 'lifetime', 'lifetime.finish', 'lifetime.start', 'middle_name', 'sex', 'title']

    >>> print (portable_repr (sorted (f_p_z._Element_Map)))
    ['Z-26:first_name', 'Z-26:last_name', 'Z-26:lifetime', 'Z-26:lifetime.finish', 'Z-26:lifetime.start', 'Z-26:middle_name', 'Z-26:phones', 'Z-26:phones::desc@3', 'Z-26:phones::extension@3', 'Z-26:phones::left.first_name@3', 'Z-26:phones::left.last_name@3', 'Z-26:phones::left.middle_name@3', 'Z-26:phones::left.title@3', 'Z-26:phones::left@3', 'Z-26:phones::right.cc@3', 'Z-26:phones::right.ndc@3', 'Z-26:phones::right.sn@3', 'Z-26:phones::right@3', 'Z-26:phones@3', 'Z-26:sex', 'Z-26:title', 'first_name', 'last_name', 'lifetime', 'lifetime.finish', 'lifetime.start', 'middle_name', 'phones', 'phones.desc', 'phones.extension', 'phones.left', 'phones.left.first_name', 'phones.left.last_name', 'phones.left.middle_name', 'phones.left.title', 'phones.right', 'phones.right.cc', 'phones.right.ndc', 'phones.right.sn', 'sex', 'title']

    >>> show_elements (f_p_z2, "Entity")
    <Entity Z-26> <Entity Z-26>
    <Field Z-26:last_name> <Entity Z-26>
    <Field Z-26:first_name> <Entity Z-26>
    <Field Z-26:middle_name> <Entity Z-26>
    <Field Z-26:title> <Entity Z-26>
    <Field_Composite Z-26:lifetime> <Entity Z-26>
    <Field Z-26:lifetime.start> <Entity Z-26>
    <Field Z-26:lifetime.finish> <Entity Z-26>
    <Field Z-26:sex> <Entity Z-26>
    <Field_Rev_Ref Z-26:phones> <Entity Z-26>
    <Entity_Rev_Ref Z-26:phones@3> <Entity_Rev_Ref Z-26:phones@3>
    <Field_Entity Z-26:phones::right@3> <Entity_Rev_Ref Z-26:phones@3>
    <Field Z-26:phones::right.cc@3> <Field_Entity Z-26:phones::right@3>
    <Field Z-26:phones::right.ndc@3> <Field_Entity Z-26:phones::right@3>
    <Field Z-26:phones::right.sn@3> <Field_Entity Z-26:phones::right@3>
    <Field Z-26:phones::extension@3> <Entity_Rev_Ref Z-26:phones@3>
    <Field Z-26:phones::desc@3> <Entity_Rev_Ref Z-26:phones@3>
    <Field_Ref_Hidden Z-26:phones::left@3> <Entity_Rev_Ref Z-26:phones@3>
    <Entity_Rev_Ref Z-26:phones/1> <Entity_Rev_Ref Z-26:phones/1>
    <Field_Entity Z-26:phones::right/1> <Entity_Rev_Ref Z-26:phones/1>
    <Field Z-26:phones::right.cc/1> <Field_Entity Z-26:phones::right/1>
    <Field Z-26:phones::right.ndc/1> <Field_Entity Z-26:phones::right/1>
    <Field Z-26:phones::right.sn/1> <Field_Entity Z-26:phones::right/1>
    <Field Z-26:phones::extension/1> <Entity_Rev_Ref Z-26:phones/1>
    <Field Z-26:phones::desc/1> <Entity_Rev_Ref Z-26:phones/1>
    <Field_Ref_Hidden Z-26:phones::left/1> <Entity_Rev_Ref Z-26:phones/1>
    <Entity_Rev_Ref Z-26:phones/2> <Entity_Rev_Ref Z-26:phones/2>
    <Field_Entity Z-26:phones::right/2> <Entity_Rev_Ref Z-26:phones/2>
    <Field Z-26:phones::right.cc/2> <Field_Entity Z-26:phones::right/2>
    <Field Z-26:phones::right.ndc/2> <Field_Entity Z-26:phones::right/2>
    <Field Z-26:phones::right.sn/2> <Field_Entity Z-26:phones::right/2>
    <Field Z-26:phones::extension/2> <Entity_Rev_Ref Z-26:phones/2>
    <Field Z-26:phones::desc/2> <Entity_Rev_Ref Z-26:phones/2>
    <Field_Ref_Hidden Z-26:phones::left/2> <Entity_Rev_Ref Z-26:phones/2>

    >>> show_elements (f_p_z2, "index")
    <Entity Z-26>
    <Field Z-26:last_name>
    <Field Z-26:first_name>
    <Field Z-26:middle_name>
    <Field Z-26:title>
    <Field_Composite Z-26:lifetime>
    <Field Z-26:lifetime.start>
    <Field Z-26:lifetime.finish>
    <Field Z-26:sex>
    <Field_Rev_Ref Z-26:phones>
    <Entity_Rev_Ref Z-26:phones@3> @3
    <Field_Entity Z-26:phones::right@3> @3
    <Field Z-26:phones::right.cc@3> @3
    <Field Z-26:phones::right.ndc@3> @3
    <Field Z-26:phones::right.sn@3> @3
    <Field Z-26:phones::extension@3> @3
    <Field Z-26:phones::desc@3> @3
    <Field_Ref_Hidden Z-26:phones::left@3> @3
    <Entity_Rev_Ref Z-26:phones/1> /1
    <Field_Entity Z-26:phones::right/1> /1
    <Field Z-26:phones::right.cc/1> /1
    <Field Z-26:phones::right.ndc/1> /1
    <Field Z-26:phones::right.sn/1> /1
    <Field Z-26:phones::extension/1> /1
    <Field Z-26:phones::desc/1> /1
    <Field_Ref_Hidden Z-26:phones::left/1> /1
    <Entity_Rev_Ref Z-26:phones/2> /2
    <Field_Entity Z-26:phones::right/2> /2
    <Field Z-26:phones::right.cc/2> /2
    <Field Z-26:phones::right.ndc/2> /2
    <Field Z-26:phones::right.sn/2> /2
    <Field Z-26:phones::extension/2> /2
    <Field Z-26:phones::desc/2> /2
    <Field_Ref_Hidden Z-26:phones::left/2> /2

    >>> show_elements (f_p_z2, "q_name")
    <Entity Z-26> None
    <Field Z-26:last_name> last_name
    <Field Z-26:first_name> first_name
    <Field Z-26:middle_name> middle_name
    <Field Z-26:title> title
    <Field_Composite Z-26:lifetime> lifetime
    <Field Z-26:lifetime.start> lifetime.start
    <Field Z-26:lifetime.finish> lifetime.finish
    <Field Z-26:sex> sex
    <Field_Rev_Ref Z-26:phones> phones
    <Entity_Rev_Ref Z-26:phones@3> phones
    <Field_Entity Z-26:phones::right@3> phones.right
    <Field Z-26:phones::right.cc@3> phones.right.cc
    <Field Z-26:phones::right.ndc@3> phones.right.ndc
    <Field Z-26:phones::right.sn@3> phones.right.sn
    <Field Z-26:phones::extension@3> phones.extension
    <Field Z-26:phones::desc@3> phones.desc
    <Field_Ref_Hidden Z-26:phones::left@3> phones.left
    <Entity_Rev_Ref Z-26:phones/1> phones
    <Field_Entity Z-26:phones::right/1> phones.right
    <Field Z-26:phones::right.cc/1> phones.right.cc
    <Field Z-26:phones::right.ndc/1> phones.right.ndc
    <Field Z-26:phones::right.sn/1> phones.right.sn
    <Field Z-26:phones::extension/1> phones.extension
    <Field Z-26:phones::desc/1> phones.desc
    <Field_Ref_Hidden Z-26:phones::left/1> phones.left
    <Entity_Rev_Ref Z-26:phones/2> phones
    <Field_Entity Z-26:phones::right/2> phones.right
    <Field Z-26:phones::right.cc/2> phones.right.cc
    <Field Z-26:phones::right.ndc/2> phones.right.ndc
    <Field Z-26:phones::right.sn/2> phones.right.sn
    <Field Z-26:phones::extension/2> phones.extension
    <Field Z-26:phones::desc/2> phones.desc
    <Field_Ref_Hidden Z-26:phones::left/2> phones.left

    >>> f_p_z2 ["Z-26:phones"]
    <Field_Rev_Ref Z-26:phones>

    >>> f_p_z2 ["Z-26:phones@3"]
    <Entity_Rev_Ref Z-26:phones@3>

    >>> f_p_z2 ["Z-26:phones/1"]
    <Entity_Rev_Ref Z-26:phones/1>

    >>> f_p_z2 ["Z-26:phones/2"]
    <Entity_Rev_Ref Z-26:phones/2>

    >>> f_p_z2_cargo = f_p_z2.as_json_cargo ["cargo"]
    >>> print (formatted (f_p_z2_cargo))
    { 'field_values' :
        { 'Z-26:first_name' : {'init' : 'Christian'}
        , 'Z-26:last_name' : {'init' : 'Tanzer'}
        , 'Z-26:lifetime.finish' : {}
        , 'Z-26:lifetime.start' : {'init' : '1959-09-26'}
        , 'Z-26:middle_name' : {}
        , 'Z-26:phones::desc/1' : {}
        , 'Z-26:phones::desc/2' : {}
        , 'Z-26:phones::desc@3' : {'init' : 'example'}
        , 'Z-26:phones::extension/1' : {}
        , 'Z-26:phones::extension/2' : {}
        , 'Z-26:phones::extension@3' : {'init' : '42'}
        , 'Z-26:phones::left/1' : {'init' : {}}
        , 'Z-26:phones::left/2' : {'init' : {}}
        , 'Z-26:phones::left@3' :
            { 'init' :
                { 'cid' : 1
                , 'display' : 'Tanzer Christian'
                , 'pid' : 1
                }
            }
        , 'Z-26:phones::right.cc/1' : {'edit' : '+43'}
        , 'Z-26:phones::right.cc/2' : {'edit' : '+43'}
        , 'Z-26:phones::right.cc@3' : {'init' : '+43'}
        , 'Z-26:phones::right.ndc/1' : {}
        , 'Z-26:phones::right.ndc/2' : {}
        , 'Z-26:phones::right.ndc@3' : {'init' : '1'}
        , 'Z-26:phones::right.sn/1' : {}
        , 'Z-26:phones::right.sn/2' : {}
        , 'Z-26:phones::right.sn@3' : {'init' : '98765432'}
        , 'Z-26:phones::right/1' : {'init' : {}}
        , 'Z-26:phones::right/2' : {'init' : {}}
        , 'Z-26:phones::right@3' :
            { 'init' :
                { 'cid' : 2
                , 'display' : '+43-1-987 654 32'
                , 'pid' : 2
                }
            }
        , 'Z-26:phones@3' :
            { 'init' :
                { 'cid' : 3
                , 'display' : 'Tanzer Christian, +43-1-987 654 32, 42'
                , 'pid' : 3
                }
            }
        , 'Z-26:sex' : {}
        , 'Z-26:title' : {}
        }
    , 'pid' : 1
    , 'sid' : 0
    , 'sigs' :
        { 'Z-26' : 'dxIDJ3yZVcgB4EOzcrzloZ-PespkJUDvqZDpNQ'
        , 'Z-26:phones/1' : '5Emb8noyfH6y9iXocwihOVKUY7Fl87CwfK_snQ'
        , 'Z-26:phones/2' : 'ABEse4QgSmUV2kHs11jPb0YZoX17UQpbPsZWTg'
        , 'Z-26:phones::right/1' : 'kBHk1wYXSwdUar1xHmKmvYCokwZLYqPrxtc-_Q'
        , 'Z-26:phones::right/2' : '7BUGMsG-u3B_iQcFEVGES3DI2bFYHBGVfYXdsA'
        , 'Z-26:phones::right@3' : 'RI8lMuuAH4Aq2IAf3BH8tKLwvhc8ZgyvLniDyg'
        , 'Z-26:phones@3' : 'luUj-F9qHmVLs2-5J14hRA_jl0uSYQDtBBhuhA'
        }
    }

    >>> for e in f_p_z.entity_elements :
    ...     print (e)
    <Entity Z-26>
    <Entity_Rev_Ref Z-26:phones@3>
    <Field_Entity Z-26:phones::right@3>

    >>> f_p_z.populate_new (f_p_z2_cargo)

    >>> for e in f_p_z.entity_elements :
    ...     print (e)
    <Entity Z-26>
    <Entity_Rev_Ref Z-26:phones@3>
    <Field_Entity Z-26:phones::right@3>
    <Entity_Rev_Ref Z-26:phones/1>
    <Field_Entity Z-26:phones::right/1>
    <Entity_Rev_Ref Z-26:phones/2>
    <Field_Entity Z-26:phones::right/2>

    >>> show_elements (f_p_z, "template_macro")
    <Entity Z-26> Entity_Form
    <Field Z-26:last_name> Field
    <Field Z-26:first_name> Field
    <Field Z-26:middle_name> Field
    <Field Z-26:title> Field
    <Field_Composite Z-26:lifetime> Field_Composite
    <Field Z-26:lifetime.start> Field
    <Field Z-26:lifetime.finish> Field
    <Field Z-26:sex> Field
    <Field_Rev_Ref Z-26:phones> Field_Rev_Ref
    <Entity_Rev_Ref Z-26:phones@3> Entity_Rev_Ref
    <Field_Entity Z-26:phones::right@3> Field_Entity
    <Field Z-26:phones::right.cc@3> Field
    <Field Z-26:phones::right.ndc@3> Field
    <Field Z-26:phones::right.sn@3> Field
    <Field Z-26:phones::extension@3> Field
    <Field Z-26:phones::desc@3> Field
    <Field_Ref_Hidden Z-26:phones::left@3> Field_Ref_Hidden
    <Entity_Rev_Ref Z-26:phones/1> Entity_Rev_Ref
    <Field_Entity Z-26:phones::right/1> Field_Entity
    <Field Z-26:phones::right.cc/1> Field
    <Field Z-26:phones::right.ndc/1> Field
    <Field Z-26:phones::right.sn/1> Field
    <Field Z-26:phones::extension/1> Field
    <Field Z-26:phones::desc/1> Field
    <Field_Ref_Hidden Z-26:phones::left/1> Field_Ref_Hidden
    <Entity_Rev_Ref Z-26:phones/2> Entity_Rev_Ref
    <Field_Entity Z-26:phones::right/2> Field_Entity
    <Field Z-26:phones::right.cc/2> Field
    <Field Z-26:phones::right.ndc/2> Field
    <Field Z-26:phones::right.sn/2> Field
    <Field Z-26:phones::extension/2> Field
    <Field Z-26:phones::desc/2> Field
    <Field_Ref_Hidden Z-26:phones::left/2> Field_Ref_Hidden

    >>> show_elements (f_p_z, "input_widget")
    <Entity Z-26> ---
    <Field Z-26:last_name> mf3_input, string
    <Field Z-26:first_name> mf3_input, string
    <Field Z-26:middle_name> mf3_input, string
    <Field Z-26:title> mf3_input, string
    <Field_Composite Z-26:lifetime> mf3_input, string
    <Field Z-26:lifetime.start> mf3_input, date
    <Field Z-26:lifetime.finish> mf3_input, date
    <Field Z-26:sex> mf3_input, named_object
    <Field_Rev_Ref Z-26:phones> mf3_input, string
    <Entity_Rev_Ref Z-26:phones@3> mf3_input, id_entity
    <Field_Entity Z-26:phones::right@3> mf3_input, id_entity
    <Field Z-26:phones::right.cc@3> mf3_input, number
    <Field Z-26:phones::right.ndc@3> mf3_input, number
    <Field Z-26:phones::right.sn@3> mf3_input, number
    <Field Z-26:phones::extension@3> mf3_input, number
    <Field Z-26:phones::desc@3> mf3_input, string
    <Field_Ref_Hidden Z-26:phones::left@3> mf3_input, hidden
    <Entity_Rev_Ref Z-26:phones/1> mf3_input, id_entity
    <Field_Entity Z-26:phones::right/1> mf3_input, id_entity
    <Field Z-26:phones::right.cc/1> mf3_input, number
    <Field Z-26:phones::right.ndc/1> mf3_input, number
    <Field Z-26:phones::right.sn/1> mf3_input, number
    <Field Z-26:phones::extension/1> mf3_input, number
    <Field Z-26:phones::desc/1> mf3_input, string
    <Field_Ref_Hidden Z-26:phones::left/1> mf3_input, hidden
    <Entity_Rev_Ref Z-26:phones/2> mf3_input, id_entity
    <Field_Entity Z-26:phones::right/2> mf3_input, id_entity
    <Field Z-26:phones::right.cc/2> mf3_input, number
    <Field Z-26:phones::right.ndc/2> mf3_input, number
    <Field Z-26:phones::right.sn/2> mf3_input, number
    <Field Z-26:phones::extension/2> mf3_input, number
    <Field Z-26:phones::desc/2> mf3_input, string
    <Field_Ref_Hidden Z-26:phones::left/2> mf3_input, hidden

    >>> _ = f_p_z ["Z-26:phones"].add ()

    >>> for e in f_p_z.entity_elements :
    ...     print (e)
    <Entity Z-26>
    <Entity_Rev_Ref Z-26:phones@3>
    <Field_Entity Z-26:phones::right@3>
    <Entity_Rev_Ref Z-26:phones/1>
    <Field_Entity Z-26:phones::right/1>
    <Entity_Rev_Ref Z-26:phones/2>
    <Field_Entity Z-26:phones::right/2>
    <Entity_Rev_Ref Z-26:phones/3>
    <Field_Entity Z-26:phones::right/3>

    >>> F_PhP   = MF3_E.Entity.Auto (scope.PAP.Person_has_Phone, id_prefix = "X")
    >>> f_PhP   = F_PhP (scope)
    >>> f_pph   = F_PhP (scope, pph)
    >>> F_PhP_s = MF3_E.Entity.Auto (scope.PAP.Person_has_Phone, id_prefix = "Y", attr_spec = { "left.middle_name" : dict (skip = 1), "right.cc" : dict (init ="49", prefilled = 1)})
    >>> f_PhP_s = F_PhP_s (scope)
    >>> F_PhP_z = MF3_E.Entity.Auto (scope.PAP.Person_has_Phone, id_prefix = "Z", attr_spec = { "left" : dict (allow_new = True, attr_selector = MOM.Attr.Selector.editable), "right" : dict (attr_selector = MOM.Attr.Selector.editable)})
    >>> f_PhP_z = F_PhP_z (scope)

    >>> show_elements_x (f_PhP_s, "id", "allow_new", filter = (Q.allow_new != None))
    Type    id           allow_new
    ============================
    F_E     Y-121:left   False
    F_E     Y-121:right  True

    >>> show_elements_x (f_PhP_z, "id", "allow_new", filter = (Q.allow_new != None))
    Type    id           allow_new
    ===========================
    F_E     Z-121:left   True
    F_E     Z-121:right  True

    >>> show_elements (f_PhP_z, "Entity")
    <Entity Z-121> <Entity Z-121>
    <Field_Entity Z-121:left> <Entity Z-121>
    <Field Z-121:left.last_name> <Field_Entity Z-121:left>
    <Field Z-121:left.first_name> <Field_Entity Z-121:left>
    <Field Z-121:left.middle_name> <Field_Entity Z-121:left>
    <Field Z-121:left.title> <Field_Entity Z-121:left>
    <Field_Composite Z-121:left.lifetime> <Field_Entity Z-121:left>
    <Field Z-121:left.lifetime.start> <Field_Entity Z-121:left>
    <Field Z-121:left.lifetime.finish> <Field_Entity Z-121:left>
    <Field Z-121:left.sex> <Field_Entity Z-121:left>
    <Field_Entity Z-121:right> <Entity Z-121>
    <Field Z-121:right.cc> <Field_Entity Z-121:right>
    <Field Z-121:right.ndc> <Field_Entity Z-121:right>
    <Field Z-121:right.sn> <Field_Entity Z-121:right>
    <Field Z-121:right.desc> <Field_Entity Z-121:right>
    <Field Z-121:extension> <Entity Z-121>
    <Field Z-121:desc> <Entity Z-121>

    >>> show_elements (f_PhP_z, "q_name")
    <Entity Z-121> None
    <Field_Entity Z-121:left> left
    <Field Z-121:left.last_name> left.last_name
    <Field Z-121:left.first_name> left.first_name
    <Field Z-121:left.middle_name> left.middle_name
    <Field Z-121:left.title> left.title
    <Field_Composite Z-121:left.lifetime> left.lifetime
    <Field Z-121:left.lifetime.start> left.lifetime.start
    <Field Z-121:left.lifetime.finish> left.lifetime.finish
    <Field Z-121:left.sex> left.sex
    <Field_Entity Z-121:right> right
    <Field Z-121:right.cc> right.cc
    <Field Z-121:right.ndc> right.ndc
    <Field Z-121:right.sn> right.sn
    <Field Z-121:right.desc> right.desc
    <Field Z-121:extension> extension
    <Field Z-121:desc> desc

    >>> show_elements (f_PhP_z, "r_name")
    <Entity Z-121> ---
    <Field_Entity Z-121:left> left
    <Field Z-121:left.last_name> last_name
    <Field Z-121:left.first_name> first_name
    <Field Z-121:left.middle_name> middle_name
    <Field Z-121:left.title> title
    <Field_Composite Z-121:left.lifetime> lifetime
    <Field Z-121:left.lifetime.start> lifetime.start
    <Field Z-121:left.lifetime.finish> lifetime.finish
    <Field Z-121:left.sex> sex
    <Field_Entity Z-121:right> right
    <Field Z-121:right.cc> cc
    <Field Z-121:right.ndc> ndc
    <Field Z-121:right.sn> sn
    <Field Z-121:right.desc> desc
    <Field Z-121:extension> extension
    <Field Z-121:desc> desc

    >>> show_elements (f_PhP, "root")
    <Entity X-121> <Entity X-121>
    <Field_Entity X-121:left> <Entity X-121>
    <Field_Entity X-121:right> <Entity X-121>
    <Field X-121:right.cc> <Entity X-121>
    <Field X-121:right.ndc> <Entity X-121>
    <Field X-121:right.sn> <Entity X-121>
    <Field X-121:extension> <Entity X-121>
    <Field X-121:desc> <Entity X-121>

    >>> show_elements (f_PhP, "Entity")
    <Entity X-121> <Entity X-121>
    <Field_Entity X-121:left> <Entity X-121>
    <Field_Entity X-121:right> <Entity X-121>
    <Field X-121:right.cc> <Field_Entity X-121:right>
    <Field X-121:right.ndc> <Field_Entity X-121:right>
    <Field X-121:right.sn> <Field_Entity X-121:right>
    <Field X-121:extension> <Entity X-121>
    <Field X-121:desc> <Entity X-121>

    >>> show_elements (f_PhP, "Entity.E_Type.type_name")
    <Entity X-121> PAP.Person_has_Phone
    <Field_Entity X-121:left> PAP.Person_has_Phone
    <Field_Entity X-121:right> PAP.Person_has_Phone
    <Field X-121:right.cc> PAP.Phone
    <Field X-121:right.ndc> PAP.Phone
    <Field X-121:right.sn> PAP.Phone
    <Field X-121:extension> PAP.Person_has_Phone
    <Field X-121:desc> PAP.Person_has_Phone

    >>> show_elements (f_PhP, "E_Type.type_name")
    <Entity X-121> PAP.Person_has_Phone
    <Field_Entity X-121:left> PAP.Person
    <Field_Entity X-121:right> PAP.Phone
    <Field X-121:right.cc> PAP.Phone
    <Field X-121:right.ndc> PAP.Phone
    <Field X-121:right.sn> PAP.Phone
    <Field X-121:extension> PAP.Person_has_Phone
    <Field X-121:desc> PAP.Person_has_Phone

    >>> show_elements (f_PhP, "attr.E_Type.type_name")
    <Entity X-121> ---
    <Field_Entity X-121:left> PAP.Person
    <Field_Entity X-121:right> PAP.Phone
    <Field X-121:right.cc> ---
    <Field X-121:right.ndc> ---
    <Field X-121:right.sn> ---
    <Field X-121:extension> ---
    <Field X-121:desc> ---

    >>> show_elements (F_PhP, "parent")
    <class Entity X-121> None
    <class Field_Entity X-121:left> <class Entity X-121>
    <class Field X-121:left.last_name> <class Field_Entity X-121:left>
    <class Field X-121:left.first_name> <class Field_Entity X-121:left>
    <class Field X-121:left.middle_name> <class Field_Entity X-121:left>
    <class Field X-121:left.title> <class Field_Entity X-121:left>
    <class Field_Entity X-121:right> <class Entity X-121>
    <class Field X-121:right.cc> <class Field_Entity X-121:right>
    <class Field X-121:right.ndc> <class Field_Entity X-121:right>
    <class Field X-121:right.sn> <class Field_Entity X-121:right>
    <class Field X-121:extension> <class Entity X-121>
    <class Field X-121:desc> <class Entity X-121>

    >>> show_elements (f_PhP, "parent")
    <Entity X-121> None
    <Field_Entity X-121:left> <Entity X-121>
    <Field_Entity X-121:right> <Entity X-121>
    <Field X-121:right.cc> <Field_Entity X-121:right>
    <Field X-121:right.ndc> <Field_Entity X-121:right>
    <Field X-121:right.sn> <Field_Entity X-121:right>
    <Field X-121:extension> <Entity X-121>
    <Field X-121:desc> <Entity X-121>

    >>> for e in f_PhP.entity_elements :
    ...     print (e)
    <Entity X-121>
    <Field_Entity X-121:right>

    >>> for e in f_PhP.field_elements :
    ...     print (e)
    <Field_Entity X-121:left>
    <Field_Entity X-121:right>
    <Field X-121:extension>
    <Field X-121:desc>

    >>> show_elements (F_PhP, "input_widget")
    <class Entity X-121> ---
    <class Field_Entity X-121:left> mf3_input, id_entity
    <class Field X-121:left.last_name> mf3_input, string
    <class Field X-121:left.first_name> mf3_input, string
    <class Field X-121:left.middle_name> mf3_input, string
    <class Field X-121:left.title> mf3_input, string
    <class Field_Entity X-121:right> mf3_input, id_entity
    <class Field X-121:right.cc> mf3_input, number
    <class Field X-121:right.ndc> mf3_input, number
    <class Field X-121:right.sn> mf3_input, number
    <class Field X-121:extension> mf3_input, number
    <class Field X-121:desc> mf3_input, string

    >>> show_elements (f_PhP, "input_widget")
    <Entity X-121> ---
    <Field_Entity X-121:left> mf3_input, id_entity
    <Field_Entity X-121:right> mf3_input, id_entity
    <Field X-121:right.cc> mf3_input, number
    <Field X-121:right.ndc> mf3_input, number
    <Field X-121:right.sn> mf3_input, number
    <Field X-121:extension> mf3_input, number
    <Field X-121:desc> mf3_input, string

    >>> show_elements (f_PhP, "template_macro")
    <Entity X-121> Entity_Form
    <Field_Entity X-121:left> Field_Entity
    <Field_Entity X-121:right> Field_Entity
    <Field X-121:right.cc> Field
    <Field X-121:right.ndc> Field
    <Field X-121:right.sn> Field
    <Field X-121:extension> Field
    <Field X-121:desc> Field

    >>> show_elements (f_PhP, "cooked")
    <Entity X-121> ---
    <Field_Entity X-121:left> None
    <Field_Entity X-121:right> None
    <Field X-121:right.cc> 43
    <Field X-121:right.ndc>
    <Field X-121:right.sn>
    <Field X-121:extension>
    <Field X-121:desc>

    >>> show_elements (f_PhP, "edit")
    <Entity X-121> ---
    <Field_Entity X-121:left>
    <Field_Entity X-121:right>
    <Field X-121:right.cc> +43
    <Field X-121:right.ndc>
    <Field X-121:right.sn>
    <Field X-121:extension>
    <Field X-121:desc>

    >>> show_elements (f_PhP_s, "edit")
    <Entity Y-121> ---
    <Field_Entity Y-121:left>
    <Field_Entity Y-121:right>
    <Field Y-121:right.cc> 49
    <Field Y-121:right.ndc>
    <Field Y-121:right.sn>
    <Field Y-121:extension>
    <Field Y-121:desc>

    >>> show_elements (f_PhP_s, "prefilled")
    <Entity Y-121> ---
    <Field_Entity Y-121:left> False
    <Field_Entity Y-121:right> False
    <Field Y-121:right.cc> 1
    <Field Y-121:right.ndc> False
    <Field Y-121:right.sn> False
    <Field Y-121:extension> False
    <Field Y-121:desc> False

    >>> show_elements (f_pph, "cooked")
    <Entity X-121> ---
    <Field_Entity X-121:left> ('tanzer', 'christian', '', '')
    <Field_Entity X-121:right> ('43', '1', '98765432')
    <Field X-121:right.cc> 43
    <Field X-121:right.ndc> 1
    <Field X-121:right.sn> 98765432
    <Field X-121:extension> 42
    <Field X-121:desc> example

    >>> show_elements (f_pph, "edit")
    <Entity X-121> ---
    <Field_Entity X-121:left> 1
    <Field_Entity X-121:right> 2
    <Field X-121:right.cc> +43
    <Field X-121:right.ndc> 1
    <Field X-121:right.sn> 98765432
    <Field X-121:extension> 42
    <Field X-121:desc> example

    >>> show_elements (f_pph, "ui_display")
    <Entity X-121> Tanzer Christian, +43-1-987 654 32, 42
    <Field_Entity X-121:left> Tanzer Christian
    <Field_Entity X-121:right> +43-1-987 654 32
    <Field X-121:right.cc> +43
    <Field X-121:right.ndc> 1
    <Field X-121:right.sn> 98765432
    <Field X-121:extension> 42
    <Field X-121:desc> example

    >>> show_elements (f_pph, "essence")
    <Entity X-121> (('tanzer', 'christian', '', ''), ('43', '1', '98765432'), '42')
    <Field_Entity X-121:left> ('tanzer', 'christian', '', '')
    <Field_Entity X-121:right> ('43', '1', '98765432')
    <Field X-121:right.cc> ('43', '1', '98765432')
    <Field X-121:right.ndc> ('43', '1', '98765432')
    <Field X-121:right.sn> ('43', '1', '98765432')
    <Field X-121:extension> (('tanzer', 'christian', '', ''), ('43', '1', '98765432'), '42')
    <Field X-121:desc> (('tanzer', 'christian', '', ''), ('43', '1', '98765432'), '42')

    >>> show_elements (f_pph, "q_name")
    <Entity X-121> None
    <Field_Entity X-121:left> left
    <Field_Entity X-121:right> right
    <Field X-121:right.cc> right.cc
    <Field X-121:right.ndc> right.ndc
    <Field X-121:right.sn> right.sn
    <Field X-121:extension> extension
    <Field X-121:desc> desc

    >>> show_elements (f_pph, "prefilled")
    <Entity X-121> ---
    <Field_Entity X-121:left> False
    <Field_Entity X-121:right> False
    <Field X-121:right.cc> False
    <Field X-121:right.ndc> False
    <Field X-121:right.sn> False
    <Field X-121:extension> False
    <Field X-121:desc> False

    >>> show_field_values (f_pph)
    { 'X-121:desc' : {'init' : 'example'}
    , 'X-121:extension' : {'init' : '42'}
    , 'X-121:left' :
        { 'init' :
            { 'cid' : 1
            , 'display' : 'Tanzer Christian'
            , 'pid' : 1
            }
        }
    , 'X-121:right' :
        { 'init' :
            { 'cid' : 2
            , 'display' : '+43-1-987 654 32'
            , 'pid' : 2
            }
        }
    , 'X-121:right.cc' : {'init' : '+43'}
    , 'X-121:right.ndc' : {'init' : '1'}
    , 'X-121:right.sn' : {'init' : '98765432'}
    }


    >>> show_field_values (f_PhP_s)
    { 'Y-121:desc' : {}
    , 'Y-121:extension' : {}
    , 'Y-121:left' : {'init' : {}}
    , 'Y-121:right' : {'init' : {}}
    , 'Y-121:right.cc' : {'edit' : '49'}
    , 'Y-121:right.ndc' : {}
    , 'Y-121:right.sn' : {}
    }


    >>> show_field_values (f_PhP_z)
    { 'Z-121:desc' : {}
    , 'Z-121:extension' : {}
    , 'Z-121:left' : {'init' : {}}
    , 'Z-121:left.first_name' : {}
    , 'Z-121:left.last_name' : {}
    , 'Z-121:left.lifetime.finish' : {}
    , 'Z-121:left.lifetime.start' : {}
    , 'Z-121:left.middle_name' : {}
    , 'Z-121:left.sex' : {}
    , 'Z-121:left.title' : {}
    , 'Z-121:right' : {'init' : {}}
    , 'Z-121:right.cc' : {'edit' : '+43'}
    , 'Z-121:right.desc' : {}
    , 'Z-121:right.ndc' : {}
    , 'Z-121:right.sn' : {}
    }

    >>> set (x.id for x in F_PhP.elements_transitive ()) >= set (x.id for x in f_PhP.elements_transitive ())
    True

    >>> list (x.id for x in f_pph.elements_transitive ()) == list (x.id for x in f_PhP.elements_transitive ())
    True

    >>> SRM     = scope.SRM
    >>> F_BiR   = MF3_E.Entity.Auto (scope.SRM.Boat_in_Regatta, id_prefix = "R")
    >>> f_bir   = F_BiR (scope, attr_spec = { "right" : dict (allow_new = True) })
    >>> f_bir_n = F_BiR (scope)

    >>> show_elements_x (f_bir, "id", "allow_new", filter = (Q.allow_new != None))
    Type    id                      allow_new
    ======================================
    F_E     R-107:left              True
    F_E     R-107:left.left         True
    F_E     R-107:right             True
    F_E     R-107:right.left        True
    F_E     R-107:right.boat_class  True
    F_E     R-107:skipper           True
    F_E     R-107:skipper.left      True
    F_E     R-107:skipper.club      True

    >>> show_elements_x (f_bir_n, "id", "allow_new", filter = (Q.allow_new != None))
    Type    id                  allow_new
    ===================================
    F_E     R-107:left          True
    F_E     R-107:left.left     True
    F_E     R-107:right         False
    F_E     R-107:skipper       True
    F_E     R-107:skipper.left  True
    F_E     R-107:skipper.club  True

    >>> show_elements_x (f_bir, "id", "Entity.id")
    Type    id                              Entity.id
    ================================================================
    E       R-107                           R-107
    F_E     R-107:left                      R-107
    F_E     R-107:left.left                 R-107:left
    F       R-107:left.left.name            R-107:left.left
    F       R-107:left.sail_number          R-107:left
    F       R-107:left.nation               R-107:left
    F       R-107:left.sail_number_x        R-107:left
    F_E     R-107:right                     R-107
    F_E     R-107:right.left                R-107:right
    F       R-107:right.left.name           R-107:right.left
    F_C     R-107:right.left.date           R-107:right.left
    F       R-107:right.left.date.start     R-107:right.left
    F       R-107:right.left.date.finish    R-107:right.left
    F_E     R-107:right.boat_class          R-107:right
    F       R-107:right.boat_class.name     R-107:right.boat_class
    F_E     R-107:skipper                   R-107
    F_E     R-107:skipper.left              R-107:skipper
    F       R-107:skipper.left.last_name    R-107:skipper.left
    F       R-107:skipper.left.first_name   R-107:skipper.left
    F       R-107:skipper.left.middle_name  R-107:skipper.left
    F       R-107:skipper.left.title        R-107:skipper.left
    F       R-107:skipper.nation            R-107:skipper
    F       R-107:skipper.mna_number        R-107:skipper
    F_E     R-107:skipper.club              R-107:skipper
    F       R-107:skipper.club.name         R-107:skipper.club
    F       R-107:place                     R-107
    F       R-107:points                    R-107
    F       R-107:yardstick                 R-107

    >>> show_elements_x (f_bir, "q_name", "r_name", "E_Type.type_name")
    Type    q_name                    r_name         E_Type.type_name
    ======================================================================
    E       None                      None           SRM.Boat_in_Regatta
    F_E     left                      left           SRM.Boat
    F_E     left.left                 left           SRM.Boat_Class
    F       left.left.name            name           SRM.Boat_Class
    F       left.sail_number          sail_number    SRM.Boat
    F       left.nation               nation         SRM.Boat
    F       left.sail_number_x        sail_number_x  SRM.Boat
    F_E     right                     right          SRM.Regatta
    F_E     right.left                left           SRM.Regatta_Event
    F       right.left.name           name           SRM.Regatta_Event
    F_C     right.left.date           date           MOM.Date_Interval_C
    F       right.left.date.start     date.start     MOM.Date_Interval_C
    F       right.left.date.finish    date.finish    MOM.Date_Interval_C
    F_E     right.boat_class          boat_class     SRM._Boat_Class_
    F       right.boat_class.name     name           SRM._Boat_Class_
    F_E     skipper                   skipper        SRM.Sailor
    F_E     skipper.left              left           PAP.Person
    F       skipper.left.last_name    last_name      PAP.Person
    F       skipper.left.first_name   first_name     PAP.Person
    F       skipper.left.middle_name  middle_name    PAP.Person
    F       skipper.left.title        title          PAP.Person
    F       skipper.nation            nation         SRM.Sailor
    F       skipper.mna_number        mna_number     SRM.Sailor
    F_E     skipper.club              club           SRM.Club
    F       skipper.club.name         name           SRM.Club
    F       place                     place          SRM.Boat_in_Regatta
    F       points                    points         SRM.Boat_in_Regatta
    F       yardstick                 yardstick      SRM.Boat_in_Regatta

    >>> show_elements_x (f_bir, "attr.e_type.type_name", "parent.E_Type.type_name")
    Type    attr.e_type.type_name  parent.E_Type.type_name
    ==================================================
    E       None                 None
    F_E     SRM.Boat_in_Regatta  SRM.Boat_in_Regatta
    F_E     SRM.Boat             SRM.Boat
    F       SRM.Boat_Class       SRM.Boat_Class
    F       SRM.Boat             SRM.Boat
    F       SRM.Boat             SRM.Boat
    F       SRM.Boat             SRM.Boat
    F_E     SRM.Boat_in_Regatta  SRM.Boat_in_Regatta
    F_E     SRM.Regatta          SRM.Regatta
    F       SRM.Regatta_Event    SRM.Regatta_Event
    F_C     SRM.Regatta_Event    SRM.Regatta_Event
    F       MOM.Date_Interval    MOM.Date_Interval_C
    F       MOM.Date_Interval_C  MOM.Date_Interval_C
    F_E     SRM.Regatta          SRM.Regatta
    F       SRM._Boat_Class_     SRM._Boat_Class_
    F_E     SRM.Boat_in_Regatta  SRM.Boat_in_Regatta
    F_E     SRM.Sailor           SRM.Sailor
    F       PAP.Person           PAP.Person
    F       PAP.Person           PAP.Person
    F       PAP.Person           PAP.Person
    F       PAP.Person           PAP.Person
    F       SRM.Sailor           SRM.Sailor
    F       SRM.Sailor           SRM.Sailor
    F_E     SRM.Sailor           SRM.Sailor
    F       SRM.Club             SRM.Club
    F       SRM.Boat_in_Regatta  SRM.Boat_in_Regatta
    F       SRM.Boat_in_Regatta  SRM.Boat_in_Regatta
    F       SRM.Boat_in_Regatta  SRM.Boat_in_Regatta

    >>> show_completers (f_bir, "q_name", "attr.completer.kind")
    Type    q_name                    attr.completer.kind
    =============================================
    F       left.left.name            Atom
    F       left.sail_number          Atom
    F       left.sail_number_x        Atom
    F       right.left.name           Atom
    F_C     right.left.date           Composite
    F       right.left.date.start     Atom
    F       right.left.date.finish    Atom
    F       right.boat_class.name     Atom
    F_E     skipper.left              Id_Entity
    F       skipper.left.last_name    Atom
    F       skipper.left.first_name   Atom
    F       skipper.left.middle_name  Atom
    F       skipper.left.title        Atom
    F       skipper.mna_number        Atom
    F_E     skipper.club              Id_Entity
    F       skipper.club.name         Atom

    >>> show_completers (f_bir, "q_name", "attr.completer.names")
    Type    q_name                    attr.completer.names
    =======================================================================================
    F       left.left.name            ('name',)
    F       left.sail_number          ('sail_number', 'left', 'nation', 'sail_number_x')
    F       left.sail_number_x        ('sail_number_x', 'left', 'sail_number', 'nation')
    F       right.left.name           ('name', 'date')
    F_C     right.left.date           ('date', 'name')
    F       right.left.date.start     ('start',)
    F       right.left.date.finish    ('finish',)
    F       right.boat_class.name     ('name',)
    F_E     skipper.left              ('left', 'nation', 'mna_number', 'club')
    F       skipper.left.last_name    ('last_name', 'first_name', 'middle_name', 'title')
    F       skipper.left.first_name   ('first_name', 'last_name', 'middle_name', 'title')
    F       skipper.left.middle_name  ('middle_name', 'last_name', 'first_name', 'title')
    F       skipper.left.title        ('title',)
    F       skipper.mna_number        ('mna_number', 'left', 'nation', 'club')
    F_E     skipper.club              ('club', 'left', 'nation', 'mna_number')
    F       skipper.club.name         ('name',)

    >>> show_completers (f_bir, "q_name", "completer.embedder")
    Type    q_name                    completer.embedder
    ===================================================================================================================
    F       left.left.name            None
    F       left.sail_number          None
    F       left.sail_number_x        None
    F       right.left.name           None
    F_C     right.left.date           None
    F       right.left.date.start     None
    F       right.left.date.finish    None
    F       right.boat_class.name     None
    F_E     skipper.left              None
    F       skipper.left.last_name    <E_Completer for <Field_Entity R-107:skipper.left>, treshold = 1, entity_p = 1>
    F       skipper.left.first_name   <E_Completer for <Field_Entity R-107:skipper.left>, treshold = 1, entity_p = 1>
    F       skipper.left.middle_name  <E_Completer for <Field_Entity R-107:skipper.left>, treshold = 1, entity_p = 1>
    F       skipper.left.title        None
    F       skipper.mna_number        None
    F_E     skipper.club              None
    F       skipper.club.name         <E_Completer for <Field_Entity R-107:skipper.club>, treshold = 1, entity_p = 1>

    >>> show_completers (f_bir, "q_name", "completer.elems")
    Type    q_name                    completer.elems
    ==================================================================================================================================================================================================================================================================================================================================================================
    F       left.left.name            (<Field R-107:left.left.name>,)
    F       left.sail_number          (<Field R-107:left.sail_number>, <Field_Entity R-107:left.left>, <Field R-107:left.nation>, <Field R-107:left.sail_number_x>)
    F       left.sail_number_x        (<Field R-107:left.sail_number_x>, <Field_Entity R-107:left.left>, <Field R-107:left.sail_number>, <Field R-107:left.nation>)
    F       right.left.name           (<Field R-107:right.left.name>, <Field R-107:right.left.date.start>, <Field R-107:right.left.date.finish>)
    F_C     right.left.date           (<Field R-107:right.left.date.start>, <Field R-107:right.left.date.finish>, <Field R-107:right.left.name>)
    F       right.left.date.start     (<Field R-107:right.left.date.start>,)
    F       right.left.date.finish    (<Field R-107:right.left.date.finish>,)
    F       right.boat_class.name     (<Field R-107:right.boat_class.name>,)
    F_E     skipper.left              (<Field_Entity R-107:skipper.left>, <Field R-107:skipper.left.last_name>, <Field R-107:skipper.left.first_name>, <Field R-107:skipper.left.middle_name>, <Field R-107:skipper.left.title>, <Field R-107:skipper.nation>, <Field R-107:skipper.mna_number>, <Field R-107:skipper.club.name>, <Field_Entity R-107:skipper.club>)
    F       skipper.left.last_name    (<Field R-107:skipper.left.last_name>, <Field_Entity R-107:skipper.left>, <Field R-107:skipper.left.first_name>, <Field R-107:skipper.left.middle_name>, <Field R-107:skipper.left.title>, <Field R-107:skipper.nation>, <Field R-107:skipper.mna_number>, <Field R-107:skipper.club.name>, <Field_Entity R-107:skipper.club>)
    F       skipper.left.first_name   (<Field R-107:skipper.left.first_name>, <Field_Entity R-107:skipper.left>, <Field R-107:skipper.left.last_name>, <Field R-107:skipper.left.middle_name>, <Field R-107:skipper.left.title>, <Field R-107:skipper.nation>, <Field R-107:skipper.mna_number>, <Field R-107:skipper.club.name>, <Field_Entity R-107:skipper.club>)
    F       skipper.left.middle_name  (<Field R-107:skipper.left.middle_name>, <Field_Entity R-107:skipper.left>, <Field R-107:skipper.left.last_name>, <Field R-107:skipper.left.first_name>, <Field R-107:skipper.left.title>, <Field R-107:skipper.nation>, <Field R-107:skipper.mna_number>, <Field R-107:skipper.club.name>, <Field_Entity R-107:skipper.club>)
    F       skipper.left.title        (<Field R-107:skipper.left.title>,)
    F       skipper.mna_number        (<Field R-107:skipper.mna_number>, <Field R-107:skipper.left.last_name>, <Field R-107:skipper.left.first_name>, <Field R-107:skipper.left.middle_name>, <Field R-107:skipper.left.title>, <Field_Entity R-107:skipper.left>, <Field R-107:skipper.nation>, <Field R-107:skipper.club.name>, <Field_Entity R-107:skipper.club>)
    F_E     skipper.club              (<Field_Entity R-107:skipper.club>, <Field R-107:skipper.club.name>, <Field R-107:skipper.left.last_name>, <Field R-107:skipper.left.first_name>, <Field R-107:skipper.left.middle_name>, <Field R-107:skipper.left.title>, <Field_Entity R-107:skipper.left>, <Field R-107:skipper.nation>, <Field R-107:skipper.mna_number>)
    F       skipper.club.name         (<Field R-107:skipper.club.name>, <Field_Entity R-107:skipper.club>, <Field R-107:skipper.left.last_name>, <Field R-107:skipper.left.first_name>, <Field R-107:skipper.left.middle_name>, <Field R-107:skipper.left.title>, <Field_Entity R-107:skipper.left>, <Field R-107:skipper.nation>, <Field R-107:skipper.mna_number>)

    >>> show_completers (f_bir, "q_name", "attr.completer.as_json_cargo")
    Type    q_name                    attr.completer.as_json_cargo
    ==============================================================================================================================
    F       left.left.name            entity_p = True, names = ['name'], treshold = 1
    F       left.sail_number          entity_p = True, names = ['sail_number', 'left', 'nation', 'sail_number_x'], treshold = 1
    F       left.sail_number_x        entity_p = True, names = ['sail_number_x', 'left', 'sail_number', 'nation'], treshold = 1
    F       right.left.name           entity_p = True, names = ['name', 'date'], treshold = 1
    F_C     right.left.date           entity_p = True, names = ['date', 'name'], treshold = 1
    F       right.left.date.start     entity_p = False, names = ['start'], treshold = 4
    F       right.left.date.finish    entity_p = False, names = ['finish'], treshold = 4
    F       right.boat_class.name     entity_p = True, names = ['name'], treshold = 1
    F_E     skipper.left              entity_p = True, names = ['left', 'nation', 'mna_number', 'club'], treshold = 1
    F       skipper.left.last_name    entity_p = True, names = ['last_name', 'first_name', 'middle_name', 'title'], treshold = 1
    F       skipper.left.first_name   entity_p = True, names = ['first_name', 'last_name', 'middle_name', 'title'], treshold = 1
    F       skipper.left.middle_name  entity_p = True, names = ['middle_name', 'last_name', 'first_name', 'title'], treshold = 1
    F       skipper.left.title        entity_p = False, names = ['title'], treshold = 0
    F       skipper.mna_number        entity_p = True, names = ['mna_number', 'left', 'nation', 'club'], treshold = 1
    F_E     skipper.club              entity_p = True, names = ['club', 'left', 'nation', 'mna_number'], treshold = 1
    F       skipper.club.name         entity_p = True, names = ['name'], treshold = 1

    >>> show_completers (f_bir, "q_name", "completer.id", "completer.as_json_cargo")
    Type    q_name                    completer.id  completer.as_json_cargo
    ========================================================================================
    F       left.left.name            2     buddies_id = 2, entity_p = True, treshold = 1
    F       left.sail_number          3     buddies_id = 3, entity_p = True, treshold = 1
    F       left.sail_number_x        3     buddies_id = 3, entity_p = True, treshold = 1
    F       right.left.name           4     buddies_id = 4, entity_p = True, treshold = 1
    F_C     right.left.date           None  buddies_id = 4, entity_p = True, treshold = 1
    F       right.left.date.start     5     buddies_id = 5, entity_p = False, treshold = 4
    F       right.left.date.finish    6     buddies_id = 6, entity_p = False, treshold = 4
    F       right.boat_class.name     7     buddies_id = 7, entity_p = True, treshold = 1
    F_E     skipper.left              1     buddies_id = 1, entity_p = True, treshold = 1
    F       skipper.left.last_name    1     buddies_id = 1, entity_p = True, treshold = 1
    F       skipper.left.first_name   1     buddies_id = 1, entity_p = True, treshold = 1
    F       skipper.left.middle_name  1     buddies_id = 1, entity_p = True, treshold = 1
    F       skipper.left.title        8     buddies_id = 8, entity_p = False, treshold = 0
    F       skipper.mna_number        1     buddies_id = 1, entity_p = True, treshold = 1
    F_E     skipper.club              1     buddies_id = 1, entity_p = True, treshold = 1
    F       skipper.club.name         1     buddies_id = 1, entity_p = True, treshold = 1

    >>> show_completers (f_bir, "q_name", "completer.id", "completer.sig")
    Type    q_name                    completer.id  completer.sig
    =======================================================
    F       left.left.name            2     (2, 1, True)
    F       left.sail_number          3     (3, 1, True)
    F       left.sail_number_x        3     (3, 1, True)
    F       right.left.name           4     (4, 1, True)
    F_C     right.left.date           None  (4, 1, True)
    F       right.left.date.start     5     (5, 4, False)
    F       right.left.date.finish    6     (6, 4, False)
    F       right.boat_class.name     7     (7, 1, True)
    F_E     skipper.left              1     (1, 1, True)
    F       skipper.left.last_name    1     (1, 1, True)
    F       skipper.left.first_name   1     (1, 1, True)
    F       skipper.left.middle_name  1     (1, 1, True)
    F       skipper.left.title        8     (8, 0, False)
    F       skipper.mna_number        1     (1, 1, True)
    F_E     skipper.club              1     (1, 1, True)
    F       skipper.club.name         1     (1, 1, True)

    >>> show_completers (f_bir, "q_name", "completer.buddies_id", "polisher.id")
    Type    q_name                    completer.buddies_id  polisher.id
    ===========================================
    F       left.left.name            2  None
    F       left.sail_number          3  9
    F       left.sail_number_x        3  None
    F       right.left.name           4  None
    F_C     right.left.date           4  None
    F       right.left.date.start     5  10
    F       right.left.date.finish    6  10
    F       right.boat_class.name     7  None
    F_E     skipper.left              1  None
    F       skipper.left.last_name    1  11
    F       skipper.left.first_name   1  12
    F       skipper.left.middle_name  1  13
    F       skipper.left.title        8  8
    F       skipper.mna_number        1  None
    F_E     skipper.club              1  None
    F       skipper.club.name         1  None

    >>> print (formatted (f_bir.as_json_cargo ["buddies"]))
    { 1 :
        [ 'R-107:skipper.club'
        , 'R-107:skipper.club.name'
        , 'R-107:skipper.left'
        , 'R-107:skipper.left.first_name'
        , 'R-107:skipper.left.last_name'
        , 'R-107:skipper.left.middle_name'
        , 'R-107:skipper.left.title'
        , 'R-107:skipper.mna_number'
        , 'R-107:skipper.nation'
        ]
    , 2 : ['R-107:left.left.name']
    , 3 :
        [ 'R-107:left.left'
        , 'R-107:left.nation'
        , 'R-107:left.sail_number'
        , 'R-107:left.sail_number_x'
        ]
    , 4 :
        [ 'R-107:right.left.date.finish'
        , 'R-107:right.left.date.start'
        , 'R-107:right.left.name'
        ]
    , 5 : ['R-107:right.left.date.start']
    , 6 : ['R-107:right.left.date.finish']
    , 7 : ['R-107:right.boat_class.name']
    , 8 : ['R-107:skipper.left.title']
    , 9 :
        [ 'R-107:left.nation'
        , 'R-107:left.sail_number'
        , 'R-107:left.sail_number_x'
        ]
    , 10 :
        [ 'R-107:right.left.date.finish'
        , 'R-107:right.left.date.start'
        ]
    , 11 : ['R-107:skipper.left.last_name']
    , 12 : ['R-107:skipper.left.first_name']
    , 13 : ['R-107:skipper.left.middle_name']
    }

    >>> show_completers_js (f_bir)
    { 1 :
        { 'buddies_id' : 1
        , 'entity_p' : True
        , 'treshold' : 1
        }
    , 2 :
        { 'buddies_id' : 2
        , 'entity_p' : True
        , 'treshold' : 1
        }
    , 3 :
        { 'buddies_id' : 3
        , 'entity_p' : True
        , 'treshold' : 1
        }
    , 4 :
        { 'buddies_id' : 4
        , 'entity_p' : True
        , 'treshold' : 1
        }
    , 5 :
        { 'buddies_id' : 5
        , 'entity_p' : False
        , 'treshold' : 4
        }
    , 6 :
        { 'buddies_id' : 6
        , 'entity_p' : False
        , 'treshold' : 4
        }
    , 7 :
        { 'buddies_id' : 7
        , 'entity_p' : True
        , 'treshold' : 1
        }
    , 8 :
        { 'buddies_id' : 8
        , 'entity_p' : False
        , 'treshold' : 0
        }
    }

    >>> show_completers (f_bir, "q_name", "completer.entity_p")
    Type    q_name                    completer.entity_p
    =========================================
    F       left.left.name            True
    F       left.sail_number          True
    F       left.sail_number_x        True
    F       right.left.name           True
    F_C     right.left.date           True
    F       right.left.date.start     False
    F       right.left.date.finish    False
    F       right.boat_class.name     True
    F_E     skipper.left              True
    F       skipper.left.last_name    True
    F       skipper.left.first_name   True
    F       skipper.left.middle_name  True
    F       skipper.left.title        False
    F       skipper.mna_number        True
    F_E     skipper.club              True
    F       skipper.club.name         True

    >>> show_completers (f_bir, "q_name", "completer.anchor")
    Type    q_name                    completer.anchor
    =========================================================================
    F       left.left.name            <Field_Entity R-107:left.left>
    F       left.sail_number          <Field_Entity R-107:left>
    F       left.sail_number_x        <Field_Entity R-107:left>
    F       right.left.name           <Field_Entity R-107:right.left>
    F_C     right.left.date           <Field_Entity R-107:right.left>
    F       right.left.date.start     <Field_Entity R-107:right.left>
    F       right.left.date.finish    <Field_Entity R-107:right.left>
    F       right.boat_class.name     <Field_Entity R-107:right.boat_class>
    F_E     skipper.left              <Field_Entity R-107:skipper>
    F       skipper.left.last_name    <Field_Entity R-107:skipper>
    F       skipper.left.first_name   <Field_Entity R-107:skipper>
    F       skipper.left.middle_name  <Field_Entity R-107:skipper>
    F       skipper.left.title        <Field_Entity R-107:skipper.left>
    F       skipper.mna_number        <Field_Entity R-107:skipper>
    F_E     skipper.club              <Field_Entity R-107:skipper>
    F       skipper.club.name         <Field_Entity R-107:skipper>

    >>> show_completers (f_bir, "q_name", "completer.fields")
    Type    q_name                    completer.fields
    ==============================================================================================================================================================================================================================================================================================
    F       left.left.name            ('R-107:left.left.name',)
    F       left.sail_number          ('R-107:left.left', 'R-107:left.nation', 'R-107:left.sail_number', 'R-107:left.sail_number_x')
    F       left.sail_number_x        ('R-107:left.left', 'R-107:left.nation', 'R-107:left.sail_number', 'R-107:left.sail_number_x')
    F       right.left.name           ('R-107:right.left.date.finish', 'R-107:right.left.date.start', 'R-107:right.left.name')
    F_C     right.left.date           ('R-107:right.left.date.finish', 'R-107:right.left.date.start', 'R-107:right.left.name')
    F       right.left.date.start     ('R-107:right.left.date.start',)
    F       right.left.date.finish    ('R-107:right.left.date.finish',)
    F       right.boat_class.name     ('R-107:right.boat_class.name',)
    F_E     skipper.left              ('R-107:skipper.club', 'R-107:skipper.club.name', 'R-107:skipper.left', 'R-107:skipper.left.first_name', 'R-107:skipper.left.last_name', 'R-107:skipper.left.middle_name', 'R-107:skipper.left.title', 'R-107:skipper.mna_number', 'R-107:skipper.nation')
    F       skipper.left.last_name    ('R-107:skipper.club', 'R-107:skipper.club.name', 'R-107:skipper.left', 'R-107:skipper.left.first_name', 'R-107:skipper.left.last_name', 'R-107:skipper.left.middle_name', 'R-107:skipper.left.title', 'R-107:skipper.mna_number', 'R-107:skipper.nation')
    F       skipper.left.first_name   ('R-107:skipper.club', 'R-107:skipper.club.name', 'R-107:skipper.left', 'R-107:skipper.left.first_name', 'R-107:skipper.left.last_name', 'R-107:skipper.left.middle_name', 'R-107:skipper.left.title', 'R-107:skipper.mna_number', 'R-107:skipper.nation')
    F       skipper.left.middle_name  ('R-107:skipper.club', 'R-107:skipper.club.name', 'R-107:skipper.left', 'R-107:skipper.left.first_name', 'R-107:skipper.left.last_name', 'R-107:skipper.left.middle_name', 'R-107:skipper.left.title', 'R-107:skipper.mna_number', 'R-107:skipper.nation')
    F       skipper.left.title        ('R-107:skipper.left.title',)
    F       skipper.mna_number        ('R-107:skipper.club', 'R-107:skipper.club.name', 'R-107:skipper.left', 'R-107:skipper.left.first_name', 'R-107:skipper.left.last_name', 'R-107:skipper.left.middle_name', 'R-107:skipper.left.title', 'R-107:skipper.mna_number', 'R-107:skipper.nation')
    F_E     skipper.club              ('R-107:skipper.club', 'R-107:skipper.club.name', 'R-107:skipper.left', 'R-107:skipper.left.first_name', 'R-107:skipper.left.last_name', 'R-107:skipper.left.middle_name', 'R-107:skipper.left.title', 'R-107:skipper.mna_number', 'R-107:skipper.nation')
    F       skipper.club.name         ('R-107:skipper.club', 'R-107:skipper.club.name', 'R-107:skipper.left', 'R-107:skipper.left.first_name', 'R-107:skipper.left.last_name', 'R-107:skipper.left.middle_name', 'R-107:skipper.left.title', 'R-107:skipper.mna_number', 'R-107:skipper.nation')

    >>> show_completers (f_bir, "q_name", "completer.field_ids")
    Type    q_name                    completer.field_ids
    ==============================================================================================================================================================================================================================================================================================
    F       left.left.name            ('R-107:left.left.name',)
    F       left.sail_number          ('R-107:left.sail_number', 'R-107:left.left', 'R-107:left.nation', 'R-107:left.sail_number_x')
    F       left.sail_number_x        ('R-107:left.sail_number_x', 'R-107:left.left', 'R-107:left.sail_number', 'R-107:left.nation')
    F       right.left.name           ('R-107:right.left.name', 'R-107:right.left.date.start', 'R-107:right.left.date.finish')
    F_C     right.left.date           ('R-107:right.left.date.start', 'R-107:right.left.date.finish', 'R-107:right.left.name')
    F       right.left.date.start     ('R-107:right.left.date.start',)
    F       right.left.date.finish    ('R-107:right.left.date.finish',)
    F       right.boat_class.name     ('R-107:right.boat_class.name',)
    F_E     skipper.left              ('R-107:skipper.left', 'R-107:skipper.left.last_name', 'R-107:skipper.left.first_name', 'R-107:skipper.left.middle_name', 'R-107:skipper.left.title', 'R-107:skipper.nation', 'R-107:skipper.mna_number', 'R-107:skipper.club.name', 'R-107:skipper.club')
    F       skipper.left.last_name    ('R-107:skipper.left.last_name', 'R-107:skipper.left', 'R-107:skipper.left.first_name', 'R-107:skipper.left.middle_name', 'R-107:skipper.left.title', 'R-107:skipper.nation', 'R-107:skipper.mna_number', 'R-107:skipper.club.name', 'R-107:skipper.club')
    F       skipper.left.first_name   ('R-107:skipper.left.first_name', 'R-107:skipper.left', 'R-107:skipper.left.last_name', 'R-107:skipper.left.middle_name', 'R-107:skipper.left.title', 'R-107:skipper.nation', 'R-107:skipper.mna_number', 'R-107:skipper.club.name', 'R-107:skipper.club')
    F       skipper.left.middle_name  ('R-107:skipper.left.middle_name', 'R-107:skipper.left', 'R-107:skipper.left.last_name', 'R-107:skipper.left.first_name', 'R-107:skipper.left.title', 'R-107:skipper.nation', 'R-107:skipper.mna_number', 'R-107:skipper.club.name', 'R-107:skipper.club')
    F       skipper.left.title        ('R-107:skipper.left.title',)
    F       skipper.mna_number        ('R-107:skipper.mna_number', 'R-107:skipper.left.last_name', 'R-107:skipper.left.first_name', 'R-107:skipper.left.middle_name', 'R-107:skipper.left.title', 'R-107:skipper.left', 'R-107:skipper.nation', 'R-107:skipper.club.name', 'R-107:skipper.club')
    F_E     skipper.club              ('R-107:skipper.club', 'R-107:skipper.club.name', 'R-107:skipper.left.last_name', 'R-107:skipper.left.first_name', 'R-107:skipper.left.middle_name', 'R-107:skipper.left.title', 'R-107:skipper.left', 'R-107:skipper.nation', 'R-107:skipper.mna_number')
    F       skipper.club.name         ('R-107:skipper.club.name', 'R-107:skipper.club', 'R-107:skipper.left.last_name', 'R-107:skipper.left.first_name', 'R-107:skipper.left.middle_name', 'R-107:skipper.left.title', 'R-107:skipper.left', 'R-107:skipper.nation', 'R-107:skipper.mna_number')

    >>> show_completers (f_bir, "q_name", "completer.etn", "completer.attr_names")
    Type    q_name                    completer.etn      completer.attr_names
    ===================================================================================================================================================================================
    F       left.left.name            SRM.Boat_Class     ('name',)
    F       left.sail_number          SRM.Boat           ('sail_number', 'left', 'nation', 'sail_number_x')
    F       left.sail_number_x        SRM.Boat           ('sail_number_x', 'left', 'sail_number', 'nation')
    F       right.left.name           SRM.Regatta_Event  ('name', 'date.start', 'date.finish')
    F_C     right.left.date           SRM.Regatta_Event  ('date.start', 'date.finish', 'name')
    F       right.left.date.start     SRM.Regatta_Event  ('date.start',)
    F       right.left.date.finish    SRM.Regatta_Event  ('date.finish',)
    F       right.boat_class.name     SRM._Boat_Class_   ('name',)
    F_E     skipper.left              SRM.Sailor         ('left', 'left.last_name', 'left.first_name', 'left.middle_name', 'left.title', 'nation', 'mna_number', 'club.name', 'club')
    F       skipper.left.last_name    SRM.Sailor         ('left.last_name', 'left', 'left.first_name', 'left.middle_name', 'left.title', 'nation', 'mna_number', 'club.name', 'club')
    F       skipper.left.first_name   SRM.Sailor         ('left.first_name', 'left', 'left.last_name', 'left.middle_name', 'left.title', 'nation', 'mna_number', 'club.name', 'club')
    F       skipper.left.middle_name  SRM.Sailor         ('left.middle_name', 'left', 'left.last_name', 'left.first_name', 'left.title', 'nation', 'mna_number', 'club.name', 'club')
    F       skipper.left.title        PAP.Person         ('title',)
    F       skipper.mna_number        SRM.Sailor         ('mna_number', 'left.last_name', 'left.first_name', 'left.middle_name', 'left.title', 'left', 'nation', 'club.name', 'club')
    F_E     skipper.club              SRM.Sailor         ('club', 'club.name', 'left.last_name', 'left.first_name', 'left.middle_name', 'left.title', 'left', 'nation', 'mna_number')
    F       skipper.club.name         SRM.Sailor         ('club.name', 'club', 'left.last_name', 'left.first_name', 'left.middle_name', 'left.title', 'left', 'nation', 'mna_number')

    >>> show_elements_x (f_p, "q_name", "completer.id", "completer.as_json_cargo")
    Type    q_name           completer.id  completer.as_json_cargo
    ===============================================================================
    E       None             None  None
    F       last_name        1     buddies_id = 1, entity_p = True, treshold = 1
    F       first_name       1     buddies_id = 1, entity_p = True, treshold = 1
    F       middle_name      1     buddies_id = 1, entity_p = True, treshold = 1
    F       title            2     buddies_id = 2, entity_p = False, treshold = 0
    F_C     lifetime         None  None
    F       lifetime.start   3     buddies_id = 3, entity_p = False, treshold = 4
    F       lifetime.finish  4     buddies_id = 4, entity_p = False, treshold = 4
    F       sex              None  None

    >>> show_elements_x (f_p, "q_name", "completer.id", "completer.sig")
    Type    q_name           completer.id  completer.sig
    ==============================================
    E       None             None  None
    F       last_name        1     (1, 1, True)
    F       first_name       1     (1, 1, True)
    F       middle_name      1     (1, 1, True)
    F       title            2     (2, 0, False)
    F_C     lifetime         None  None
    F       lifetime.start   3     (3, 4, False)
    F       lifetime.finish  4     (4, 4, False)
    F       sex              None  None

    >>> show_completers (f_p, "q_name", "completer.name", "completer.entity_p")
    Type   q_name           completer.name   completer.entity_p
    ================================================
    F      last_name        last_name        True
    F      first_name       first_name       True
    F      middle_name      middle_name      True
    F      title            title            False
    F      lifetime.start   lifetime.start   False
    F      lifetime.finish  lifetime.finish  False

    >>> show_completers (f_p, "q_name", "completer.anchor")
    Type   q_name           completer.anchor
    =======================================
    F      last_name        <Entity X-26>
    F      first_name       <Entity X-26>
    F      middle_name      <Entity X-26>
    F      title            <Entity X-26>
    F      lifetime.start   <Entity X-26>
    F      lifetime.finish  <Entity X-26>

    >>> show_completers (f_p, "q_name", "completer.field_ids")
    Type   q_name           completer.field_ids
    =================================================================================================
    F      last_name        ('X-26:last_name', 'X-26:first_name', 'X-26:middle_name', 'X-26:title')
    F      first_name       ('X-26:first_name', 'X-26:last_name', 'X-26:middle_name', 'X-26:title')
    F      middle_name      ('X-26:middle_name', 'X-26:last_name', 'X-26:first_name', 'X-26:title')
    F      title            ('X-26:title',)
    F      lifetime.start   ('X-26:lifetime.start',)
    F      lifetime.finish  ('X-26:lifetime.finish',)

    >>> show_completers (f_p, "q_name", "completer.etn", "completer.attr_names")
    Type   q_name           completer.etn  completer.attr_names
    =========================================================================================
    F      last_name        PAP.Person  ('last_name', 'first_name', 'middle_name', 'title')
    F      first_name       PAP.Person  ('first_name', 'last_name', 'middle_name', 'title')
    F      middle_name      PAP.Person  ('middle_name', 'last_name', 'first_name', 'title')
    F      title            PAP.Person  ('title',)
    F      lifetime.start   PAP.Person  ('lifetime.start',)
    F      lifetime.finish  PAP.Person  ('lifetime.finish',)

    >>> show_completers_js (f_p)
    { 1 :
        { 'buddies_id' : 1
        , 'entity_p' : True
        , 'treshold' : 1
        }
    , 2 :
        { 'buddies_id' : 2
        , 'entity_p' : False
        , 'treshold' : 0
        }
    , 3 :
        { 'buddies_id' : 3
        , 'entity_p' : False
        , 'treshold' : 4
        }
    , 4 :
        { 'buddies_id' : 4
        , 'entity_p' : False
        , 'treshold' : 4
        }
    }

    >>> show_elements_x (f_bir, "q_name", "field_elements")
    Type    q_name                    field_elements
    =============================================================================================================================================================================================
    E       None                      (<Field_Entity R-107:left>, <Field_Entity R-107:right>, <Field_Entity R-107:skipper>, <Field R-107:place>, <Field R-107:points>, <Field R-107:yardstick>)
    F_E     left                      (<Field_Entity R-107:left.left>, <Field R-107:left.sail_number>, <Field R-107:left.nation>, <Field R-107:left.sail_number_x>)
    F_E     left.left                 (<Field R-107:left.left.name>,)
    F       left.left.name            ()
    F       left.sail_number          ()
    F       left.nation               ()
    F       left.sail_number_x        ()
    F_E     right                     (<Field_Entity R-107:right.left>, <Field_Entity R-107:right.boat_class>)
    F_E     right.left                (<Field R-107:right.left.name>, <Field R-107:right.left.date.start>, <Field R-107:right.left.date.finish>)
    F       right.left.name           ()
    F_C     right.left.date           (<Field R-107:right.left.date.start>, <Field R-107:right.left.date.finish>)
    F       right.left.date.start     ()
    F       right.left.date.finish    ()
    F_E     right.boat_class          (<Field R-107:right.boat_class.name>,)
    F       right.boat_class.name     ()
    F_E     skipper                   (<Field_Entity R-107:skipper.left>, <Field R-107:skipper.nation>, <Field R-107:skipper.mna_number>, <Field_Entity R-107:skipper.club>)
    F_E     skipper.left              (<Field R-107:skipper.left.last_name>, <Field R-107:skipper.left.first_name>, <Field R-107:skipper.left.middle_name>, <Field R-107:skipper.left.title>)
    F       skipper.left.last_name    ()
    F       skipper.left.first_name   ()
    F       skipper.left.middle_name  ()
    F       skipper.left.title        ()
    F       skipper.nation            ()
    F       skipper.mna_number        ()
    F_E     skipper.club              (<Field R-107:skipper.club.name>,)
    F       skipper.club.name         ()
    F       place                     ()
    F       points                    ()
    F       yardstick                 ()

    >>> show_elements_x (f_p, "q_name", "field_elements")
    Type    q_name           field_elements
    =======================================================================================================================================================================================================
    E       None             (<Field X-26:last_name>, <Field X-26:first_name>, <Field X-26:middle_name>, <Field X-26:title>, <Field X-26:lifetime.start>, <Field X-26:lifetime.finish>, <Field X-26:sex>)
    F       last_name        ()
    F       first_name       ()
    F       middle_name      ()
    F       title            ()
    F_C     lifetime         (<Field X-26:lifetime.start>, <Field X-26:lifetime.finish>)
    F       lifetime.start   ()
    F       lifetime.finish  ()
    F       sex              ()

    >>> show_completers (f_bir, "q_name", "completer.own_elems")
    Type    q_name                    completer.own_elems
    ==================================================================================================================================================================================================================================================================================================================================================================
    F       left.left.name            (<Field R-107:left.left.name>,)
    F       left.sail_number          (<Field R-107:left.sail_number>, <Field_Entity R-107:left.left>, <Field R-107:left.nation>, <Field R-107:left.sail_number_x>)
    F       left.sail_number_x        (<Field R-107:left.sail_number_x>, <Field_Entity R-107:left.left>, <Field R-107:left.sail_number>, <Field R-107:left.nation>)
    F       right.left.name           (<Field R-107:right.left.name>, <Field R-107:right.left.date.start>, <Field R-107:right.left.date.finish>)
    F_C     right.left.date           (<Field R-107:right.left.date.start>, <Field R-107:right.left.date.finish>)
    F       right.left.date.start     (<Field R-107:right.left.date.start>,)
    F       right.left.date.finish    (<Field R-107:right.left.date.finish>,)
    F       right.boat_class.name     (<Field R-107:right.boat_class.name>,)
    F_E     skipper.left              (<Field_Entity R-107:skipper.left>, <Field R-107:skipper.left.last_name>, <Field R-107:skipper.left.first_name>, <Field R-107:skipper.left.middle_name>, <Field R-107:skipper.left.title>, <Field R-107:skipper.nation>, <Field R-107:skipper.mna_number>, <Field R-107:skipper.club.name>, <Field_Entity R-107:skipper.club>)
    F       skipper.left.last_name    (<Field R-107:skipper.left.last_name>, <Field R-107:skipper.left.first_name>, <Field R-107:skipper.left.middle_name>, <Field R-107:skipper.left.title>)
    F       skipper.left.first_name   (<Field R-107:skipper.left.first_name>, <Field R-107:skipper.left.last_name>, <Field R-107:skipper.left.middle_name>, <Field R-107:skipper.left.title>)
    F       skipper.left.middle_name  (<Field R-107:skipper.left.middle_name>, <Field R-107:skipper.left.last_name>, <Field R-107:skipper.left.first_name>, <Field R-107:skipper.left.title>)
    F       skipper.left.title        (<Field R-107:skipper.left.title>,)
    F       skipper.mna_number        (<Field R-107:skipper.mna_number>, <Field R-107:skipper.left.last_name>, <Field R-107:skipper.left.first_name>, <Field R-107:skipper.left.middle_name>, <Field R-107:skipper.left.title>, <Field_Entity R-107:skipper.left>, <Field R-107:skipper.nation>, <Field R-107:skipper.club.name>, <Field_Entity R-107:skipper.club>)
    F_E     skipper.club              (<Field_Entity R-107:skipper.club>, <Field R-107:skipper.club.name>, <Field R-107:skipper.left.last_name>, <Field R-107:skipper.left.first_name>, <Field R-107:skipper.left.middle_name>, <Field R-107:skipper.left.title>, <Field_Entity R-107:skipper.left>, <Field R-107:skipper.nation>, <Field R-107:skipper.mna_number>)
    F       skipper.club.name         (<Field R-107:skipper.club.name>,)

    >>> show_completers (f_p, "q_name", "completer.own_elems")
    Type   q_name           completer.own_elems
    =========================================================================================================================
    F      last_name        (<Field X-26:last_name>, <Field X-26:first_name>, <Field X-26:middle_name>, <Field X-26:title>)
    F      first_name       (<Field X-26:first_name>, <Field X-26:last_name>, <Field X-26:middle_name>, <Field X-26:title>)
    F      middle_name      (<Field X-26:middle_name>, <Field X-26:last_name>, <Field X-26:first_name>, <Field X-26:title>)
    F      title            (<Field X-26:title>,)
    F      lifetime.start   (<Field X-26:lifetime.start>,)
    F      lifetime.finish  (<Field X-26:lifetime.finish>,)

    >>> EVT = scope.EVT
    >>> RR  = EVT.Recurrence_Rule
    >>> RS  = EVT.Recurrence_Spec

    >>> ev  = EVT.Event (p, p.lifetime, ("00:00", "23:59"), raw = True)
    >>> rs  = RS (ev)
    >>> rr  = RR (rs, desc = "Birthday", unit = "Yearly", raw = True)

    >>> F_E = MF3_E.Entity.Auto (EVT.Event, id_prefix = "E", attr_spec = dict (recurrence = dict (include_rev_refs = ("rules", ))), include_rev_refs = ("recurrence", ))
    >>> f_e = F_E (scope, ev)

    >>> show_elements (f_e, "ui_display")
    <Entity E-63> Tanzer Christian, 1959-09-26, 00:00 - 23:59
    <Field_Entity E-63:left> Tanzer Christian
    <Field_Composite E-63:date> 1959-09-26
    <Field E-63:date.start> 1959-09-26
    <Field E-63:date.finish>
    <Field_Composite E-63:time> 00:00 - 23:59
    <Field E-63:time.start> 00:00
    <Field E-63:time.finish> 23:59
    <Field_Entity E-63:calendar>
    <Field E-63:detail>
    <Field E-63:short_title>
    <Field_Rev_Ref E-63:recurrence> Birthday, 1959-09-26, 1, Yearly
    <Entity_Rev_Ref E-63:recurrence@6> Birthday, 1959-09-26, 1, Yearly
    <Field E-63:recurrence::dates@6>
    <Field E-63:recurrence::date_exceptions@6>
    <Field_Rev_Ref E-63:recurrence::rules@6> Birthday, 1959-09-26, 1, Yearly
    <Entity_Rev_Ref E-63:recurrence::rules@6@7> Birthday, 1959-09-26, 1, Yearly
    <Field E-63:recurrence::rules::is_exception@6@7>
    <Field E-63:recurrence::rules::desc@6@7> Birthday
    <Field E-63:recurrence::rules::start@6@7> 1959-09-26
    <Field E-63:recurrence::rules::finish@6@7>
    <Field E-63:recurrence::rules::period@6@7> 1
    <Field E-63:recurrence::rules::unit@6@7> Yearly
    <Field E-63:recurrence::rules::week_day@6@7>
    <Field E-63:recurrence::rules::count@6@7>
    <Field E-63:recurrence::rules::restrict_pos@6@7>
    <Field E-63:recurrence::rules::month_day@6@7>
    <Field E-63:recurrence::rules::month@6@7>
    <Field E-63:recurrence::rules::week@6@7>
    <Field E-63:recurrence::rules::year_day@6@7>
    <Field E-63:recurrence::rules::easter_offset@6@7>
    <Field_Ref_Hidden E-63:recurrence::rules::left@6@7>
    <Field_Ref_Hidden E-63:recurrence::left@6>

    >>> show_ui_allow (f_pph)
    <Field_Entity X-121:left>                False  True False
    <Field_Entity X-121:right>               False  True  True

    >>> show_ui_allow (f_bir)
    <Field_Entity R-107:left>                False  True  True
    <Field_Entity R-107:right>               False  True False
    <Field_Entity R-107:skipper>             False  True  True

"""

_test_max_rev_ref = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> scope.db_meta_data.dbid = '2d802327-5c99-49ca-9af7-2ddc6b4c648b'

    >>> EVT = scope.EVT
    >>> F_E = MF3_E.Entity.Auto (EVT.Event, id_prefix = "E", attr_spec = dict (recurrence = dict (include_rev_refs = ("rules", ))), include_rev_refs = ("recurrence", ))
    >>> f_e = F_E (scope)
    >>> _   = f_e ["recurrence"].add ()

    >>> show_elements (f_e, "max_rev_ref")
    <Entity E-63> ---
    <Field_Entity E-63:left> ---
    <Field_Composite E-63:date> ---
    <Field E-63:date.start> ---
    <Field E-63:date.finish> ---
    <Field_Composite E-63:time> ---
    <Field E-63:time.start> ---
    <Field E-63:time.finish> ---
    <Field_Entity E-63:calendar> ---
    <Field E-63:detail> ---
    <Field E-63:short_title> ---
    <Field_Rev_Ref E-63:recurrence> 1
    <Entity_Rev_Ref E-63:recurrence/1> ---
    <Field E-63:recurrence::dates/1> ---
    <Field E-63:recurrence::date_exceptions/1> ---
    <Field_Rev_Ref E-63:recurrence::rules/1> 2147483648
    <Field_Ref_Hidden E-63:recurrence::left/1> ---

"""

_test_single_primary = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> scope.db_meta_data.dbid = '2d802327-5c99-49ca-9af7-2ddc6b4c648b'

    >>> SRM       = scope.SRM
    >>> attr_spec = dict              (left = dict (allow_new = False))
    >>> F_B       = MF3_E.Entity.Auto (scope.SRM.Boat, id_prefix = "S")
    >>> F_B_r     = MF3_E.Entity.Auto (scope.SRM.Boat, id_prefix = "S_r", attr_spec = attr_spec)
    >>> F_RiR     = MF3_E.Entity.Auto (scope.SRM.Regatta_in_Ranking, id_prefix = "S")
    >>> f_b       = F_B               (scope)
    >>> f_b_r     = F_B_r             (scope)
    >>> f_rir     = F_RiR             (scope)

    >>> print (formatted (f_b.as_json_cargo))
    { 'buddies' :
        { 1 : ['S-77:left.name']
        , 2 :
            [ 'S-77:left'
            , 'S-77:nation'
            , 'S-77:sail_number'
            , 'S-77:sail_number_x'
            ]
        , 3 :
            [ 'S-77:nation'
            , 'S-77:sail_number'
            , 'S-77:sail_number_x'
            ]
        }
    , 'cargo' :
        { 'field_values' :
            { 'S-77:left' : {'init' : {}}
            , 'S-77:left.name' : {}
            , 'S-77:name' : {}
            , 'S-77:nation' : {}
            , 'S-77:sail_number' : {}
            , 'S-77:sail_number_x' : {}
            }
        , 'sid' : 0
        , 'sigs' :
            { 'S-77' : 'ZcPnd3XmEiQBwPFLaIEG8dYta8GmKltEfN3DIA'
            , 'S-77:left' : 'YU6_-d3stUkDuwFxCIIMjONm715KxB9HmFCQeg'
            }
        }
    , 'checkers' : {}
    , 'completers' :
        { 1 :
            { 'buddies_id' : 1
            , 'entity_p' : True
            , 'treshold' : 1
            }
        , 2 :
            { 'buddies_id' : 2
            , 'entity_p' : True
            , 'treshold' : 1
            }
        }
    }

    >>> print (formatted (f_b_r.as_json_cargo))
    { 'buddies' :
        { 1 :
            [ 'S_r-77:left'
            , 'S_r-77:nation'
            , 'S_r-77:sail_number'
            , 'S_r-77:sail_number_x'
            ]
        , 2 :
            [ 'S_r-77:nation'
            , 'S_r-77:sail_number'
            , 'S_r-77:sail_number_x'
            ]
        }
    , 'cargo' :
        { 'field_values' :
            { 'S_r-77:left' : {'init' : {}}
            , 'S_r-77:name' : {}
            , 'S_r-77:nation' : {}
            , 'S_r-77:sail_number' : {}
            , 'S_r-77:sail_number_x' : {}
            }
        , 'sid' : 0
        , 'sigs' : {'S_r-77' : 'm-dmxBk2iMRIvPAdpdFfBHda8CmQ1D0tIJ6_dQ'}
        }
    , 'checkers' : {}
    , 'completers' :
        { 1 :
            { 'buddies_id' : 1
            , 'entity_p' : True
            , 'treshold' : 1
            }
        }
    }

    >>> print (formatted (f_rir.as_json_cargo))
    { 'buddies' :
        { 1 :
            [ 'S-113:left'
            , 'S-113:right'
            ]
        }
    , 'cargo' :
        { 'field_values' :
            { 'S-113:factor' : {'edit' : '1.0'}
            , 'S-113:left' : {'init' : {}}
            , 'S-113:right' : {'init' : {}}
            }
        , 'sid' : 0
        , 'sigs' : {'S-113' : 'XiX4D4xdzkGe3I-4hLwepj9yB4W6GUWuxDOS6Q'}
        }
    , 'checkers' : {}
    , 'completers' :
        { 1 :
            { 'buddies_id' : 1
            , 'entity_p' : True
            , 'treshold' : 1
            }
        , 2 :
            { 'buddies_id' : 1
            , 'entity_p' : True
            , 'treshold' : 0
            }
        }
    }

    >>> show_elements (f_b, "Entity")
    <Entity S-77> <Entity S-77>
    <Field_Entity S-77:left> <Entity S-77>
    <Field S-77:left.name> <Field_Entity S-77:left>
    <Field S-77:sail_number> <Entity S-77>
    <Field S-77:nation> <Entity S-77>
    <Field S-77:sail_number_x> <Entity S-77>
    <Field S-77:name> <Entity S-77>

    >>> show_elements (f_b_r, "Entity")
    <Entity S_r-77> <Entity S_r-77>
    <Field_Entity S_r-77:left> <Entity S_r-77>
    <Field S_r-77:sail_number> <Entity S_r-77>
    <Field S_r-77:nation> <Entity S_r-77>
    <Field S_r-77:sail_number_x> <Entity S_r-77>
    <Field S_r-77:name> <Entity S_r-77>

    >>> sorted (f_b_r ["S_r-77:left"].attr_map.items ())
    [('name', <Field S_r-77:left.name>)]

    >>> f_b_r_l_n = f_b_r ["S_r-77:left.name"]
    >>> f_b_r_l_n.attr.completer.MF3 (f_b_r_l_n)
    <Completer for <Field S_r-77:left.name>, treshold = 1, entity_p = 1>

    >>> show_elements (f_rir, "completer")
    <Entity S-113> None
    <Field_Entity S-113:left> <E_Completer for <Field_Entity S-113:left>, treshold = 1, entity_p = 1>
    <Field_Entity S-113:right> <E_Completer for <Field_Entity S-113:right>, treshold = 0, entity_p = 1>
    <Field S-113:factor> None

    >>> f_rir_r = f_rir ["S-113:right"]
    >>> f_rir_r.completer
    <E_Completer for <Field_Entity S-113:right>, treshold = 0, entity_p = 1>

    >>> f_rir_r.completer.elems
    (<Field_Entity S-113:right>, <Field_Entity S-113:left>)

    >>> f_rir_r_n = f_rir ["S-113:right.name"]
    >>> f_rir_r_n.attr.completer.MF3 (f_rir_r_n)
    <Completer for <Field S-113:right.name>, treshold = 0, entity_p = 1>

"""

_test_skip = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> scope.db_meta_data.dbid = '2d802327-5c99-49ca-9af7-2ddc6b4c648b'

    >>> def skip_snx (v) :
    ...     return dict (attr_spec = { "left.sail_number_x" : dict (skip = v) })

    >>> F_BiR_X   = MF3_E.Entity.Auto (scope.SRM.Boat_in_Regatta, id_prefix = "X")
    >>> F_BiR_N   = MF3_E.Entity.Auto (scope.SRM.Boat_in_Regatta, id_prefix = "N", ** skip_snx (1))

    >>> f_bir_x_x = F_BiR_X (scope, ** skip_snx (0))
    >>> f_bir_x_n = F_BiR_X (scope, ** skip_snx (1))
    >>> f_bir_n_x = F_BiR_N (scope, ** skip_snx (0))
    >>> f_bir_n_n = F_BiR_N (scope, ** skip_snx (1))

    >>> list (F_BiR_X   ["left"].elements_transitive ()) [-1]
    <class Field X-107:left.sail_number_x>

    >>> list (F_BiR_N   ["left"].elements_transitive ()) [-1]
    <class Field N-107:left.nation>

    >>> list (f_bir_x_x ["left"].elements_transitive ()) [-1]
    <Field X-107:left.sail_number_x>

    >>> list (f_bir_x_n ["left"].elements_transitive ()) [-1]
    <Field X-107:left.nation>

    >>> list (f_bir_n_x ["left"].elements_transitive ()) [-1]
    <Field N-107:left.sail_number_x>

    >>> list (f_bir_n_n ["left"].elements_transitive ()) [-1]
    <Field N-107:left.nation>

"""

__test__ = Scaffold.create_test_dict \
    ( dict
        ( cls_structure  = _test_cls_structure
        , element        = _test_element
        , max_rev_ref    = _test_max_rev_ref
        , single_primary = _test_single_primary
        , skip           = _test_skip
        )
    )

### __END__ GTW.__test__.MF3
