# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package _GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    _GTW.__test__._SAW_test_functions
#
# Purpose
#    Support functions for testings SAW features
#
# Revision Dates
#    14-Aug-2013 (CT) Creation
#    26-Aug-2013 (CT) Add `show_key_o_p`, `show_sequence`
#    18-Sep-2013 (CT) Add `show_query` (uses `compile` to show `params`)
#    27-Jan-2014 (CT) Factor `formatted` to `MOM.DBW.SAW.Q_Result`
#    12-Mar-2015 (CT) Add `fixed_booleans` for sqlalchemy 0.9.8
#     5-Feb-2016 (CT) Factor `show_table`
#     3-Jun-2016 (CT) Add `show_esf_query`
#    31-Jul-2016 (CT) Move test functions from `SAW_QX` in here
#     4-Aug-2016 (CT) Change default `pred` to filter `_SAT_Desc_`
#    20-Oct-2016 (CT) Add `show_table_ancestors`, `show_table_summary`
#    ««revision-date»»···
#--

from   __future__                   import division, print_function
from   __future__                   import absolute_import, unicode_literals

from   _GTW.__test__.Test_Command   import esf_completer

from   _MOM.import_MOM              import MOM, Q
from   _MOM._DBW._SAW               import QX

from   _TFL                         import TFL
from   _TFL.portable_repr           import portable_repr
from   _TFL.predicate               import first, split_hst, rsplit_hst
from   _TFL.pyk                     import pyk

import _TFL.Regexp

import itertools
nl     = chr (10)
indent = "  " * 2
sk     = lambda x   : (x.type_name, x.i_rank, )
pred   = lambda ETW : ETW.e_type.PNS is not None

def fixed_booleans (qf) :
    if not isinstance (qf, pyk.string_types) :
        qf = pyk.text_type (qf)
    return qf.replace ("WHERE 0 = 1", "WHERE false")
# end def fixed_booleans

def formatted_column (c) :
    tail = []
    c_MOM_Kind = getattr (c, "MOM_Kind", None)
    if c_MOM_Kind :
        tail.append \
            ( "%s %s %s"
            % ( c_MOM_Kind.__class__.__name__
              , c_MOM_Kind.attr.typ
              , getattr (c_MOM_Kind, "name", c_MOM_Kind)
              )
            )
    else :
        tail.append ("-" * 10)
    if c.primary_key :
        tail.append ("primary")
    if c.foreign_keys :
        tail.extend \
            (formatted_foreign_key (fk) for fk in sorted (c.foreign_keys))
    if c_MOM_Kind and isinstance (c_MOM_Kind.attr, MOM.Attr._A_Id_Entity_) :
        tail.append (portable_repr (c.type))
    try :
        typ = str (c.type).capitalize ()
    except Exception :
        typ = c.type.__class__.__name__
    return ("Column %-25s : %-20s %s" % (c.name, typ, " ".join (tail))).strip ()
# end def formatted_column

def formatted_foreign_key (fk) :
    result = str (fk).replace ("(u'", "('")
    return result
# end def formatted_foreign_key

def formatted_select (ETW, name = "select", select = None) :
    sep = nl + indent
    if select is None :
        select = getattr (ETW, name, None)
    if select is None :
        return "No '%s'" % (name, )
    text = str (select)
    def _gen (lines, indent = 7) :
        s = "," + sep + (" " * indent)
        inner_indent = " " * (indent - 7)
        inner_sep    = "\n" + inner_indent
        for l in lines :
            if "," in l :
                comps = sorted (c.strip () for c in l.split (","))
                yield s.join (comps)
            elif "JOIN" in l :
                rerep = TFL.Re_Replacer \
                    ( "((?:[A-Z]+ )*JOIN)"
                    , "\n       \\1"
                    )
                p  = rerep (l)
                ps = list (x.rstrip () for x in p.split ("\n"))
                p  = inner_indent + inner_sep.join (ps)
                yield p
            elif "WHERE" in l :
                rerep = TFL.Re_Replacer \
                    ( "((?:\s+)*(?:AND|OR)\s+)"
                    , "\n       \\1"
                    )
                p  = rerep (l)
                ps = list (x.rstrip () for x in p.split ("\n"))
                p  = inner_indent + inner_sep.join (ps)
                yield p
            else :
                yield l
    gindent = 7
    head, _, tail  = split_hst  (text, " ")
    t_head, t_sep, t_tail = split_hst (tail, "\nFROM (SELECT")
    if t_sep :
        head = sep.join ((" ".join ((head, t_head)), t_sep.strip ()))
        tail, t_sep, t_tail_tip = rsplit_hst (t_tail, ")")
        ttt_lines = t_tail_tip.split (nl)
        gindent += 6
    lines  = tail.split (nl)
    result = " ".join \
        ((head, sep.join (x.rstrip () for x in _gen (lines, gindent))))
    if t_sep :
        r_tail = sep.join (x.rstrip () for x in _gen (ttt_lines))
        result = sep.join (( result, " " * 5 + t_sep + r_tail))
    return result.rstrip ()
# end def formatted_select

def formatted_table (ST, nl, indent) :
    sep   = nl + indent
    def _gen () :
        for c in ST.columns :
            yield formatted_column (c)
    return sep.join (x.rstrip () for x in sorted (_gen ()))
# end def formatted_table

def show_ancestors (apt, pred = pred) :
    sk = lambda x : (x.e_type.i_rank, )
    for ETW in sorted (pyk.itervalues (apt._SAW.et_map), key = sk) :
        if not pred (ETW) :
            continue
        T = ETW.e_type
        xs = ("%-36s" % (T.type_name), )
        if ETW.ancestors :
            xs += ("<" , " < ".join ("%-16s" % (a.type_name, ) for a in ETW.ancestors).rstrip ())
        print (" ".join (xs).rstrip ())
# end def show_ancestors

_ignore_kinds = set \
    (( "_Co_Base_", "_Computed_Mixin_", "_Query_", "_Typed_Collection_Mixin_"
     , "Id_Entity_Reference_Mixin", "Kind"
    ))

def _kind_mro (kind, ignore = _ignore_kinds) :
    return \
        ( c.__name__ for c in kind.__class__.__mro__
        if  issubclass (c, MOM.Attr.Kind)
        and "__" not in c.__name__
        and c.__name__ not in ignore
        )
# end def _kind_mro

def show_attr_mro (ET) :
    def show (ET, level = 1) :
        in0 = "  " * (level)
        in1 = "  " * (level + 1)
        for name, kind in sorted (pyk.iteritems (ET.attributes)) :
            if isinstance (kind, MOM.Attr.Auto_Cached) or not kind.show_in_ui :
                continue
            amro  = ", ".join (_kind_mro (kind))
            tail  = ("-> %s" % (kind.E_Type.type_name, )) \
                if isinstance (kind.E_Type, MOM.Meta.M_E_Type) else ""
            lin1  = ("%s%-20s %s" % (in0, name, tail)).rstrip ()
            print ("%s\n%s%s" % (lin1, in1, amro))
            if kind.is_composite :
                show (kind.attr.E_Type, level + 1)
    print (ET.type_name)
    show (ET)
# end def show_attr_mro

def show_attr_wrappers (apt, pred = pred) :
    def show (W, level = 0) :
        qas = W.q_able_attrs_o
        in0 = "  " * (level + bool (level))
        if qas :
            in1 = in0 + " " * (level + 1 + (not level))
            in2 = in1 + "    "
            print ("%s%s" % (in0, W.type_name))
            for name, aw in sorted (pyk.iteritems (qas)) :
                if not getattr (aw.kind, "show_in_ui", True) : continue
                amro = ", ".join (_kind_mro (aw.kind))
                print \
                    ( "%s%s : %s\n%s%s"
                    % (in1, aw.__class__.__name__, aw.kind, in2, amro)
                    )
                if aw.q_able_attrs_o :
                    show (aw, level + 1)
        elif W.e_type.relevant_root :
            print ("%s%s <-- %s" % (in0, W.type_name, W.parent.type_name))
    sk = lambda x : (x.e_type.i_rank, )
    for ETW in sorted (pyk.itervalues (apt._SAW.et_map), key = sk) :
        if not pred (ETW) :
            continue
        show (ETW)
# end def show_attr_wrappers

def show_columns (apt, ET, q) :
    qr = apt.DBW.PNS.Q_Result.E_Type (apt [ET], _strict = False)
    qx = QX.Mapper (qr) (q)
    print ("QX." + qx.__class__.__name__, ET, " : ", q)
    for c in qx._columns :
        print (" ", c)
# end def show_columns

def show_esf_query (scope, AQ, trigger, value, qdct = {}) :
    completer = esf_completer (scope, AQ, trigger, value, qdct)
    show_query (completer.query ())
# end def show_esf_query

def show_joins (apt, ET, q) :
    qr = apt.DBW.PNS.Q_Result.E_Type (apt [ET], _strict = False)
    qx = QX.Mapper (qr) (q)
    try :
        qx.XS_FILTER ### might trigger additional joins
    except Exception :
        pass
    print (ET, " : ", q)
    for j in qx.JOINS :
        print \
            ( " ", "%-5.5s" % j.joiner.__name__.upper ()
            , " = ".join (str (c) for c in j.cols)
            )
# end def show_joins

def show_key_o_p (apt) :
    def _show (k) :
        return getattr (k, "name", None)
    for ETW in apt._SAW.e_types_t :
        if ETW.key_o or ETW.key_p :
            print \
                ( ( "%-40s : %-15s %-15s"
                  % (ETW.type_name, _show (ETW.key_o), _show (ETW.key_p))
                  ).rstrip ()
                )
# end def show_key_o_p

def show_q_able (apt, pred = pred) :
    def _gen (ETW) :
        for k, q in sorted (pyk.iteritems (ETW.q_able_attrs)) :
            if not q.kind.show_in_ui : continue
            if k == q.attr.name :
                ### filter attribute-aliases
                yield str (q)
                if q.q_able_attrs :
                    for k, q in sorted (pyk.iteritems (q.q_able_attrs)) :
                        if not q.kind.show_in_ui : continue
                        if not q.columns :
                            yield str (q)
    sk = lambda x : (x.e_type.i_rank, )
    for ETW in sorted (pyk.itervalues (apt._SAW.et_map), key = sk):
        if not pred (ETW) :
            continue
        print (ETW)
        print (" ", "\n  ".join (_gen (ETW)))
# end def show_q_able

def show_q_able_names (apt, pred = pred) :
    def _gen (q_able_attrs, level = 0) :
        for k, q in sorted (pyk.iteritems (q_able_attrs)) :
            if not q.kind.show_in_ui : continue
            if k == q.attr.name :
                ### filter attribute-aliases
                yield "%s%-30s: %s" % ("    " * level, k, ", ".join (q.q_able_names))
                if q.q_able_attrs :
                    for x in _gen (q.q_able_attrs, level + 1) :
                        yield x
    sk = lambda x : (x.e_type.i_rank, )
    for ETW in sorted (pyk.itervalues (apt._SAW.et_map), key = sk):
        if not pred (ETW) :
            continue
        print (ETW)
        print (" ", "\n  ".join (_gen (ETW.q_able_attrs)))
# end def show_q_able_names

def show_qc_map (apt, pred = pred) :
    def _show (QC, indent = 4) :
        if QC.Map :
            for k, v in sorted (pyk.iteritems (QC.Map)) :
                print (("%-30s: %.80s" % (" " * indent + k, v)).rstrip ())
                if isinstance (v, QC.__class__) :
                    _show (v, indent + 4)
    sk = lambda x : (x.e_type.i_rank, )
    for ETW in sorted (pyk.itervalues (apt._SAW.et_map), key = sk):
        if not pred (ETW) :
            continue
        if ETW.sa_tables :
            print (ETW)
            _show (ETW.QC)
# end def show_qc_map

def show_query (qr) :
    print (fixed_booleans (qr.formatted ()))
# end def show_query

def show_qx (qx, level = 0) :
    print (QX.display (qx, level = 0))
# end def show_qx

def show_root_table (apt, pred = pred) :
    sk = lambda x : (x.e_type.i_rank, )
    for ETW in sorted (pyk.itervalues (apt._SAW.et_map), key = sk):
        if not pred (ETW) :
            continue
        T = ETW.e_type
        print (("%-36s %s" % (T.type_name, ETW.root_table)).rstrip ())
# end def show_root_table

def show_selects (apt, name = "select", pred = pred) :
    sk = lambda x : (x.e_type.i_rank, )
    for ETW in sorted (pyk.itervalues (apt._SAW.et_map), key = sk):
        if not pred (ETW) :
            continue
        T = ETW.e_type
        if ETW.has_relevant_tables :
            second = "" if T.relevant_root is T \
                else (T.relevant_root.type_name if T.relevant_root else "")
            head   = ("%s %s" % (T.type_name, second)).strip ()
            print \
                ( "%s%s" % (head, nl), "  "
                , fixed_booleans (formatted_select (ETW, name = name))
                )
# end def show_selects

def show_sequence (apt) :
    for ETW in apt._SAW.e_types_t :
        seq = ETW.sequence
        if seq:
            print ("%-40s : %s" % (ETW.type_name, seq.seq_name))
# end def show_sequence

def show_sequences (apt) :
    for ETW in apt._SAW.e_types_t :
        seqs = ", ".join (s.seq_name for s in ETW.sequences)
        if seqs :
            print ("%-40s : %s" % (ETW.type_name, seqs))
# end def show_sequences

def show_table (apt, ETW) :
    T      = ETW.e_type
    ST     = ETW.sa_table
    second = ("(%s)" % (ETW.parent.type_name, )) if ETW.parent else ""
    third  = "" if T.relevant_root is T \
              else (T.relevant_root and T.relevant_root.type_name)
    head   = (" ".join ((T.type_name, second, third or ""))).strip ()
    head   = ("%s <Table %s>" % (head, ETW.sa_table)).strip ()
    print \
        ( "%s%s" % (head, nl), "  "
        , formatted_table (ETW.sa_table, nl, indent)
        )
# end def show_table

def show_tables (apt, pred = pred) :
    for ETW in apt._SAW.e_types_t :
        if not pred (ETW) :
            continue
        show_table (apt, ETW)
    for seq in apt._SAW.sequences :
        print \
            ( "<Table for %s>%s" % (seq.attr, nl), "  "
            , formatted_table (seq.sa_table, nl, indent)
            )
# end def show_tables

def show_table_ancestors (apt, pred = pred) :
    for ETW in apt._SAW.e_types_t :
        if not pred (ETW) :
            continue
        fmt = "%s /%d"
        ts  = (fmt % (t, len (t.columns)) for t in reversed (ETW.sa_tables_strict))
        print ("  <  ".join (ts).rstrip ())
# end def show_table_ancestors

def show_table_summary (apt) :
    for ETW in apt._SAW.e_types_t :
        T    = ETW.e_type
        ST   = ETW.sa_table
        print ("%-40s %-40s %3d %3d" % (T.type_name, ST, len (ST.columns), len (ETW.db_attrs_o)))
# end def show_table_summary

def show_xs_filter (apt, ET, q) :
    qr = apt.DBW.PNS.Q_Result.E_Type (apt [ET], _strict = False)
    qx = QX.Mapper (qr) (q)
    print (ET, " : ", q)
    print ("   ", qx.XS_FILTER)
# end def show_xs_filter

### __END__ _GTW.__test__._SAW_test_functions
