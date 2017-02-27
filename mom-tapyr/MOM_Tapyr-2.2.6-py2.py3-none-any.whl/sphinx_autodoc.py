# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.sphinx_autodoc
#
# Purpose
#    Extension of Sphinx autodoc extension
#
# Revision Dates
#    12-Aug-2015 (CT) Creation
#    ...
#    22-Sep-2015 (CT) Factor `TFL.sphinx_autodoc`
#    13-Nov-2015 (CT) Pass explicit `key` to `sorted`
#    10-Dec-2015 (CT) Redefine `MOM_Attr_Type_Documenter._extra_doc`
#    11-Dec-2015 (CT) Add `Choices` to `_e_type_attr`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _MOM                     import MOM
from   _TFL                     import TFL

from   _MOM.import_MOM          import *

from   _TFL.Decorator           import eval_function_body
from   _TFL.pyk                 import pyk
from   _TFL                     import sos
from   _TFL._Meta.Once_Property import Once_Property

import _TFL._Meta.M_Class
import _TFL._Meta.Object
import _TFL.sphinx_autodoc

import sphinx.ext.autodoc
from   sphinx.ext               import autodoc

@eval_function_body
def _add_to_python_domain () :
    from sphinx.domains import python
    D = python.PythonDomain
    D.object_types.update \
        ( predicate = python.ObjType (python.l_('predicate'), 'pred', 'obj')
        )
    D.directives.update \
        ( predicate = python.PyClassmember
        )
    D.roles.update \
        ( pred      = python.PyXRefRole ()
        )

class _E_Type_Mapper_ (TFL.Meta.Object) :

    def __init__ (self) :
        self._app_type_map = {}
        self._e_type_map   = {}
    # end def __init__

    def app_type (self, Essence) :
        PNS  = Essence.PNS
        map  = self._app_type_map
        name = PNS.__name__
        try :
            result = map [name]
        except KeyError :
            result = map [name] = self._create_app_type (PNS, name)
        return result
    # end def app_type

    def autodoc_special_attr_getter (self, obj, name, * defargs) :
        if (   isinstance (obj, MOM.Meta.M_E_Mixin)
           and not isinstance (obj, MOM.Meta._M_E_Type_Id_RC_)
           ) :
            obj = self.e_type (obj)
        return autodoc.safe_getattr(obj, name, *defargs)
    # end def autodoc_special_attr_getter

    def e_type (self, Essence) :
        apt = self.app_type (Essence)
        return apt [Essence.type_name]
    # end def e_type

    def _create_app_type (self, PNS, name) :
        from   _MOM._EMS.Hash         import Manager as EMS
        from   _MOM._DBW._HPS.Manager import Manager as DBW
        PNS._Import_All ()
        return MOM.App_Type (name, PNS).Derived (EMS, DBW)
    # end def _create_app_type

    def __getitem__ (self, key) :
        return self.e_type (key)
    # end def __getitem__

# end class _E_Type_Mapper_

E_Type_Mapper = _E_Type_Mapper_ ()

class MOM_Class_Documenter (TFL.sphinx_autodoc.Class_Documenter) :
    """Specialized Documenter for MOM classes defining essential types"""

    _applies_to_metas      = (MOM.Meta.M_E_Mixin, )
    _MOM_ET                = None
    _MOM_skip_names        = set \
        ( [ "E_Spec", "Essence", "E_Type", "Graph_Type", "M_E_Type", "P_Type"
          , "auto_derived_root", "epk_sig_root", "relevant_root", "PNS"
          ]
        )

    def format_signature (self) :
        ### for MOM E_Types, `__init__` always has signature (* args, **kw)
        ### which isn't terribly useful, use `epkified_ckd.args` instead
        ET = self._MOM_ET
        try :
            args = ET.epkified_ckd.args
        except AttributeError :
            pass
        else :
            self.args = ", ".join ((args, "** kw"))
        return self.__super.format_signature ()
    # end def format_signature

    def _after_import_object (self) :
        self._MOM_ET = E_Type_Mapper [self.object]
        self.options.pop ("show-inheritance", None)
    # end def _after_import_object

    def _dl_element (self, term, * lines, ** kw) :
        indent = kw.pop ("indent", "")
        def _gen (term, lines, indent) :
            yield indent + term
            indent += "  "
            last    = term
            for line in lines :
                l = pyk.decoded (line)
                if l :
                    yield indent + l
                elif last :
                    yield l
                last = l
            if l :
                yield ""
        return list (_gen (term, lines or ["—"], indent))
    # end def _dl_element

    def _document_member_p (self, name, member, isattr) :
        result = not \
            (  isinstance (member, MOM.Prop.Kind)
            or name in self._MOM_skip_names
            )
        return result
    # end def _document_member_p

    def _extra_doc (self) :
        ET = self._MOM_ET
        return self._e_type_doc (ET)
    # end def _extra_doc

    def _e_type_attr (self, ET, ak, indent, electric, prefix, ETX = None) :
        if ETX is None :
            ETX    = ET
        at         = ak.attr
        a_doc      = self._e_type_attr_doc
        a_ref      = self._e_type_attr_ref
        p_ref      = self._e_type_pred_ref
        dle        = self._dl_element
        _own       = at.name in ET._Attributes._own_names
        electric_p = electric or ak.electric
        a_name     = ".".join ((prefix, ak.name)) if prefix else ak.name
        result     = ["%s.. attribute:: %s" % (indent, a_name), ""]
        indent    += "  "
        has_role_name = \
            (   isinstance (at, MOM.Attr.A_Link_Role)
            and at.role_name
            and not ak.electric
            )
        if has_role_name :
            result.extend \
                ( [ "%sCan also be accessed with the role name ``%s``"
                    % (indent, at.role_name)
                  , ""
                  ]
                )
        if at.ui_name.lower () != at.name :
            result.extend (dle (":UI name:", ak.ui_name, indent = indent))
        typ  = self._e_type_attr_typ (ET, ak)
        mxl = getattr (at, "max_length", None)
        if mxl :
            typ = "%s (maximum length: %s)" % (typ, mxl)
        ts  = [typ]
        mnv = getattr (at, "min_value", None)
        if mnv is not None :
            ts.extend (dle (":Minimum value:", mnv, indent = "    "))
        mxv = getattr (at, "max_value", None)
        if mxv is not None :
            ts.extend (dle (":Maximum value:", mxv, indent = "    "))
        result.extend (dle (":Type:",    * ts,           indent = indent))
        result.extend (dle (":Kind:",    ak.kind,        indent = indent))
        if at.Choices :
            choices = ", ".join (at.Raw_Choices)
            result.extend \
                (dle (":Choices:",       choices,        indent = indent))
        if not electric_p :
            if ak.raw_default != "" :
                result.extend \
                    (dle (":Default:",   ak.raw_default, indent = indent))
            if at.E_Type is None :
                exv = getattr (ak, "example", None)
                if exv is not None and exv != "" :
                    result.extend \
                        (dle (":Example:", exv,          indent = indent))
            result.extend \
                (dle (":Is required:",   ak.is_required, indent = indent))
            _changeable = "Only during initialization" \
                if ak.is_settable and not ak.is_changeable else ak.is_changeable
            result.extend \
                (dle (":Is changeable:", _changeable,    indent = indent))
        if at.description :
            ds = a_doc (at.description, indent)
            result.extend \
                (dle (":Description:",   * ds,           indent = indent))
        if at.explanation and _own :
            es = a_doc (at.explanation, indent)
            result.extend \
                (dle (":Explanation:",   * es,           indent = indent))
        if ak.syntax and not electric_p :
            ss = a_doc (ak.syntax, indent)
            result.extend \
                (dle (":Syntax:",        * ss,           indent = indent))
        if isinstance (at, MOM.Attr._A_Composite_) :
            nas = \
                [ "Nested attributes of composite attribute type %s"
                  % self._e_type_attr_typ (ET, ak)
                , ""
                ]
            nas.extend \
                ( * self._e_type_attrs
                    (at.E_Type, at.E_Type.ui_attr, prefix = a_name, ETX = ETX)
                )
            result.extend \
                (dle (":Attributes:",    * nas,          indent = indent))
        if at.predicates :
            prs = ", ".join \
                (   p_ref (ETX, p.name, prefix)
                for p in sorted (at.predicates, key = Q.name)
                )
            result.extend \
                (dle (":Predicates:",    prs,            indent = indent))
        result.append ("")
        return result
    # end def _e_type_attr

    def _e_type_attr_doc (self, doc, indent) :
        result = []
        if doc :
            result = autodoc.prepare_docstring (doc)
            if indent :
                result = [((indent + l) if l else l) for l in result]
        return result
    # end def _e_type_attr_doc

    def _e_type_attr_ref (self, ET, attr_name, prefix = None) :
        if ET.auto_derived_p and not attr_name in ET._Attributes._own_names :
            ET = ET.auto_derived_root
        attr_name_x = ".".join ((prefix, attr_name)) if prefix else attr_name
        return ":attr:`%s<%s.%s.%s>`" % \
            (attr_name, ET.__module__, ET.type_base_name, attr_name_x)
    # end def _e_type_attr_ref

    def _e_type_attr_typ (self, ET, ak) :
        result = ak.typ
        if ak.E_Type and not isinstance (ak.attr, MOM.Attr._A_Composite_) :
            result = self._e_type_ref (ak.E_Type, ak.typ)
        return result
    # end def _e_type_attr_typ

    def _e_type_attrs \
            ( self, ET, attrs
            , heading = None, leader = None, indent = ""
            , electric = False, prefix = None, ETX = None
            ) :
        result = self._e_type_attrs_inner \
            (ET, attrs, heading, leader, indent, electric, prefix, ETX)
        if result :
            result = [self._e_type_attr_doc ("\n".join (result), indent)]
        return result or []
    # end def _e_type_attrs

    def _e_type_attrs_edit (self, ET) :
        adp    = ET.auto_derived_p
        attrs  = ET.edit_attr
        leader = None
        result = []
        if attrs and not ET.is_partial :
            leader = self._e_type_attrs_table (ET, attrs)
        if adp :
            _own   = ET._Attributes._own_names
            attrs  = tuple (a for a in attrs if a.name in _own)
        if attrs or leader :
            result = self._e_type_attrs \
                (ET, attrs, "Editable attributes", leader, electric = adp)
        return result
    # end def _e_type_attrs_edit

    def _e_type_attrs_inner \
            ( self, ET, attrs
            , heading = None, leader = None, indent = ""
            , electric = False, prefix = None, ETX = None
            ) :
        result = []
        if heading :
            result.extend (self._heading (ET, heading, indent))
            if leader :
                result.extend (["", leader, ""])
        for ak in attrs :
            result.extend \
                (self._e_type_attr (ET, ak, indent, electric, prefix, ETX))
        return result
    # end def _e_type_attrs_inner

    def _e_type_attrs_q_able (self, ET) :
        attrs  = ET.q_able_no_edit
        _own   = ET._Attributes._own_names
        result = []
        if attrs :
            heading   = "Queryable attributes"
            leader    = None
            own_attrs = [a for a in attrs if a.name in _own]
            if len (attrs) > len (own_attrs) :
                def _gen_parents (ET) :
                    for p in ET.parents :
                        if p.q_able_no_edit :
                            ### filter out intermediate ancestors without
                            ### q_able_no_edit attributes of their own
                            ### --> refer to their parents instead
                            own = p._Attributes._own_names
                            if [a for a in p.q_able_no_edit if a.name in own] :
                                yield p
                            else :
                                for mp in _gen_parents (p) :
                                    yield mp
                parents = list (TFL.uniq (_gen_parents (ET)))
                if parents :
                    leader  = "For inherited %s see also %s" % \
                        ( heading.lower ()
                        , ", ".join
                            (   self._heading_ref (p, heading, p.type_name)
                            for p in parents
                            )
                        )
            result = self._e_type_attrs \
                ( ET, own_attrs if leader else attrs, heading, leader
                , electric = True
                )
        return result
    # end def _e_type_attrs_q_able

    def _e_type_attrs_table (self, ET, attrs) :
        indent = "    "
        sep    = "\n" + indent
        names  = ("name", "type", "kind", "required", "default")
        def _csv (self, ET, names, attrs, sep) :
            import csv
            a_ref   = self._e_type_attr_ref
            a_typ   = self._e_type_attr_typ
            body    = pyk.StringIO ()
            head    = pyk.StringIO ()
            bw      = csv.DictWriter (body, names)
            hw      = csv.DictWriter (head, names)
            for ak in attrs :
                ad  = dict \
                    ( name     = a_ref (ET, ak.name)
                    , type     = a_typ (ET, ak)
                    , kind     = ak.kind
                    , required = ak.is_required
                    , default  = ak.raw_default
                    )
                bw.writerow (ad)
            hw.writerow (dict ((n, n) for n in names))
            result = \
                ( pyk.decoded (head.getvalue ().strip ())
                , sep.join
                    (   l.strip ()
                    for l in pyk.decoded (body.getvalue ()).split ("\n")
                    )
                )
            return result
        head, body = _csv (self, ET, names, attrs, sep)
        result     = sep.join \
            ( [ ".. csv-table::"
              , ":header: " + head
              , ":class: Attr-Table"
              , ""
              , body
              ]
            )
        return result
    # end def _e_type_attrs_table

    def _e_type_cross_refs (self, ET) :
        Ref_Map = getattr (ET, "Ref_Map", {})
        a_ref   = self._e_type_attr_ref
        t_ref   = self._e_type_ref
        for cret in sorted (Ref_Map, key = Q.type_name) :
            if cret.show_in_ui :
                rats = sorted (Ref_Map [cret])
                crd  = "%s: %s" % \
                    (t_ref (cret), ", ".join (a_ref (cret, ra) for ra in rats))
                lra  = ET.link_ref_map.get (cret)
                if lra is not None :
                    crd += " [%s]" % (a_ref (ET, lra.name))
                yield crd
    # end def _e_type_cross_refs

    def _e_type_doc (self, ET) :
        dle    = self._dl_element
        ref    = self._e_type_ref
        tnd    = ET.type_name
        adp    = ET.auto_derived_p
        if ET.is_partial :
            tnd += " [partial type]"
        result = [dle ("Type name", tnd)]
        if ET.relevant_root and (ET.is_partial or ET.relevant_root is not ET) :
            result.append (dle ("Relevant root", ref (ET.relevant_root)))
        if ET.parents :
            ps = tuple ("* "+ ref (p) for p in ET.parents)
            result.append (dle ("Parents", * ps))
        children = tuple \
            (c for tn, c in pyk.iteritems (ET.children) if not c.immaterial)
        if children :
            sk = TFL.Sorted_By ()
            cs = tuple (("* " + ref (c)) for c in sorted (children, key = sk))
            result.append (dle ("Children", * cs))
        rs = tuple ("* " + r for r in self._e_type_cross_refs (ET))
        if rs :
            result.append (dle ("Reverse references", * rs))
        if not adp :
            result.extend (self._e_type_doc_x  (ET, "__doc_attr_head__"))
        result.extend (self._e_type_attrs_edit (ET))
        if not adp :
            result.extend (self._e_type_attrs_q_able (ET))
            result.extend (self._e_type_doc_x  (ET, "__doc_attr_tail__"))
            result.extend (self._e_type_doc_x  (ET, "__doc_pred_head__"))
        o_preds = ET._Predicates._pred_kind ["object"]
        if adp :
            _own    = ET._Predicates._own_names
            o_preds = tuple (p for p in o_preds if p.name in _own)
        if o_preds :
            result.extend \
                ( self._e_type_preds
                    ( ET, o_preds
                    , heading = "Object predicates"
                    , leader  =
                        ":class:`Object predicates<_MOM._Pred.Kind.Object>` "
                        "must be satisfied at all times. "
                        "They are checked whenever the value of one or "
                        "more essential attributes is set or changed."
                    )
                )
        if not adp :
            result.extend (self._e_type_doc_x (ET, "__doc_pred_tail__"))
        return result
    # end def _e_type_doc

    def _e_type_doc_x (self, ET, name) :
        result = []
        doc = getattr (ET, name, None)
        if doc is not None :
            result = [autodoc.prepare_docstring (doc)]
        return result
    # end def _e_type_doc_x

    def _e_type_pred (self, ET, pk, indent, prefix, ETX = None) :
        if ETX is None :
            ETX = ET
        pt      = pk.pred
        a_doc   = self._e_type_attr_doc
        a_ref   = self._e_type_attr_ref
        p_ref   = self._e_type_pred_ref
        dle     = self._dl_element
        p_name  = ".".join ((prefix, pt.name)) if prefix else pt.name
        t_name  = ".".join ((prefix, pt.__class__.__name__)) \
            if prefix else pt.__class__.__name__
        result  = ["%s.. predicate:: %s" % (indent, p_name), ""]
        indent += "  "
        typ     = ":class:`~_MOM._Pred.Type.%s`" % (t_name, )
        result.extend (dle (":Type:",    typ,            indent = indent))
        if pk.attrs :
            ats = ", ".join (a_ref (ETX, a, prefix) for a in pk.attrs)
            result.extend \
                (dle (":Attributes:",    ats,            indent = indent))
        if pt.assertion :
            ass = a_doc (pt.assertion, indent)
            result.extend \
                (dle (":Condition:",     * ass,          indent = indent))
        if pt.description :
            ds = a_doc (pt.description, indent)
            result.extend \
                (dle (":Description:",   * ds,           indent = indent))
        if pt.explanation :
            es = a_doc (pt.explanation, indent)
            result.extend \
                (dle (":Explanation:",   * es,           indent = indent))
        if pt.bindings :
            bs = self._e_type_pred_bindings (ET, pt.bindings, indent + "  ")
            result.extend \
                (dle (":Bindings:",      * bs,           indent = indent))
        if pt.predicates :
            ak = ET.attr_prop (pt.attributes [0])
            if ak :
                PT  = ak.E_Type
                nps = \
                    [ "Checks the predicates of composite attribute type %s"
                    % self._e_type_attr_typ (PT, ak)
                    , ""
                    ]
                nps.extend \
                    ( * self._e_type_preds
                        ( PT, PT._Predicates._pred_kind [pk.kind]
                        , prefix = ".".join ((prefix, ak.name))
                            if prefix else ak.name
                        , ETX = ETX
                        )
                    )
                result.extend \
                    (dle (":Predicates:",    * nps,      indent = indent))
        result.append ("")
        return result
    # end def _e_type_pred

    def _e_type_pred_bindings (self, ET, bindings, indent) :
        def _gen (self, ET, bindings) :
            a_doc   = self._e_type_attr_doc
            dle     = self._dl_element
            for k, v in sorted (pyk.iteritems (bindings)) :
                vs  = a_doc (v, indent)
                for l in dle (":%s:" % k, * vs, indent = indent) :
                    yield l
        return tuple (_gen (self, ET, bindings))
    # end def _e_type_pred_bindings

    def _e_type_pred_ref (self, ET, pred_name, prefix = None) :
        if ET.auto_derived_p and not pred_name in ET._Predicates._own_names :
            ET = ET.auto_derived_root
        pred_name_x = ".".join ((prefix, pred_name)) if prefix else pred_name
        return ":pred:`%s<%s.%s.%s>`" % \
            (pred_name, ET.__module__, ET.type_base_name, pred_name_x)
    # end def _e_type_pred_ref

    def _e_type_preds \
            ( self, ET, preds
            , heading = None, leader = None, indent = ""
            , prefix = None, ETX = None
            ) :
        result = self._e_type_preds_inner \
            (ET, preds, heading, leader, indent, prefix, ETX)
        if result :
            result = [self._e_type_attr_doc ("\n".join (result), indent)]
        return result or []
    # end def _e_type_preds

    def _e_type_preds_inner \
            ( self, ET, preds
            , heading = None, leader = None, indent = ""
            , prefix = None, ETX = None
            ) :
        result = []
        if heading :
            result.extend (self._heading (ET, heading, indent))
            if leader :
                result.extend (["", leader, ""])
        for pk in preds :
            result.extend (self._e_type_pred (ET, pk, indent, prefix, ETX))
        return result
    # end def _e_type_preds_inner

    def _e_type_ref (self, ET, typ = None) :
        return ":class:`%s<%s.%s>`" % \
            (typ or ET.type_name, ET.__module__, ET.type_base_name)
    # end def _e_type_ref

    def _find_signature (self, * args, ** kw) :
        ### inherited `_find_signature` calls `get_doc` --> called twice!!
        ### OTOH, for MOM E_Types the __init__ signature doesn't contain any
        ### useful information anyway
        pass
    # end def _find_signature

    def _heading (self, ET, heading, indent = "") :
        result = \
            [ "%s.. _`%s`:" % (indent, self._heading_id (ET, heading))
            , ""
            , "%s**%s**" % (indent, heading)
            , ""
            ]
        return result
    # end def _heading

    def _heading_id (self, ET, heading) :
        return "%s+%s" % (ET.type_name, heading.lower ().replace (" ", "-"))
    # end def _heading_id

    def _heading_ref (self, ET, heading, text = None) :
        format = ":ref:`%(text)s<%(ref)s>`" if text else ":ref:`%(ref)s`"
        ref    = self._heading_id (ET, heading)
        return format % dict (ref = ref, text = text)
    # end def _heading_ref

# end class MOM_Class_Documenter

class MOM_Attr_Type_Documenter (TFL.sphinx_autodoc.Class_Documenter) :
    """Class documenter for MOM classes defining attribute types."""

    _applies_to_classes    = (MOM.Attr.A_Attr_Type, )
    _extra_doc_p           = False
    _MOM_skip_names        = set \
        ( [ "A_Type"
          ]
        )

    def _extra_doc (self) :
        cls = self.object
        map = cls.__dict__.get ("_Doc_Map_")
        def _gen () :
            own = map.OWN
            if map.__doc__ and own :
                yield autodoc.prepare_docstring (map.__doc__)
            for k, v in sorted (own) :
                vs = list ("  %s" % (l, ) for l in v.split ("\n"))
                yield [".. attribute:: %s" % k, ""] + vs
        result = list (_gen ()) if map and not self._extra_doc_p else ()
        self._extra_doc_p = True
        return result
    # end def _extra_doc

    def _document_member_p (self, name, member, isattr) :
        return name not in self._MOM_skip_names
    # end def _document_member_p

# end class MOM_Attr_Type_Documenter

def setup (app):
    autodoc.AutoDirective._special_attrgetters \
        [MOM.Meta.M_E_Mixin] = E_Type_Mapper.autodoc_special_attr_getter
    return {'version': "0.7", 'parallel_read_safe': True}
# end def setup

### __END__ MOM.sphinx_autodoc
