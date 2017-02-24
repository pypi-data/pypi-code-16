# -*- coding: utf-8 -*-
# Copyright (C) 2011-2016 Mag. Christian Tanzer All rights reserved
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
#    MOM.Q_Exp
#
# Purpose
#    Extend TFL.Q_Exp to support MOM-specific query expressions,
#    e.g., for raw values
#
# Revision Dates
#    19-Jul-2011 (CT) Creation
#    19-Jul-2011 (MG) `_name` converted to `Once_Property`
#    13-Sep-2011 (CT) All Q_Exp internal classes renamed to `_«name»_`
#     8-Jul-2013 (CT) Derive `_RAW_DESC_` from `object`, not `property`
#    19-Jul-2013 (CT) Derive `Raw_Attr_Query` from `Attr_Query`;
#                     set `Q_Exp.Base.RAW` to `Raw_Attr_Query ()`;
#                     remove `_RAW_` and `_RAW_DESC_` (nice simplification)
#    30-Aug-2013 (CT) Remove `SET`
#     4-Apr-2014 (CT) Use `TFL.Q_Exp.Base`, not `TFL.Attr_Query ()`
#    26-Aug-2014 (CT) Change `_Get_Raw_._getter` to allow composite `key`
#     9-Sep-2014 (CT) Rename from `MOM.Q_Exp_Raw` to `MOM.Q_Exp`
#     9-Sep-2014 (CT) Redefine `Base`, `_Get_`;
#                     add `_Get_._E_Type_Restriction_`, `_Get_.RAW`
#    11-Sep-2014 (CT) Add `_E_Type_Restriction_.__getitem__`; add doctest
#     7-Aug-2015 (CT) Add documentation
#    10-Aug-2015 (CT) Continue adding documentation
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    24-May-2016 (CT) Override `Base.__getattr__` to handle type restrictions
#    ««revision-date»»···
#--

from   __future__               import unicode_literals

from   _MOM                     import MOM
from   _TFL                     import TFL
from   _TFL.pyk                 import pyk

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.predicate           import rsplit_hst

import _TFL.Decorator
import _TFL.Q_Exp

class _MOM_Base_ (TFL.Q_Exp.Base) :
    """Query generator supporting :mod:`~_TFL.Q_Exp` query expressions plus RAW
       queries and queries with type restrictions.

       .. _`Raw queries`:

       **Raw queries**

       A Q-expression like ``Q.foo`` refers the
       :attr:`cooked value<_MOM._Attr.Type.A_Attr_Type.needs_raw_value>`
       of the attribute named ``foo``. To define a Q-expression referring
       to the :attr:`raw value<_MOM._Attr.Type.A_Attr_Type.needs_raw_value>`
       of an attribute, Q.RAW.foo can be used:

       >>> Q.RAW.foo.bar.qux
       Q.RAW.foo.bar.qux

       >>> Q.foo.RAW.bar.qux
       Q.RAW.foo.bar.qux

       >>> Q.foo.bar.RAW.qux
       Q.RAW.foo.bar.qux

       >>> Q.foo.bar.qux.RAW
       Q.RAW.foo.bar.qux

       .. _`Type restrictions`:

       **Type restrictions**

       MOM supports polymorphic attributes, i.e., attributes that refer to a
       partial type or a non-partial type with descendent classes. A
       Q-expression referring to a polymorphic attribute is restricted to the
       attributes of the attribute's polymorphic type.

       For instance, ``PAP.Subject`` is the ancestor of ``PAP.Person`` and
       ``PAP.Company``. A Q-expression for an polymorphic attribute ``manager``
       referring to instances of ``PAP.Subject`` is restricted to the
       attributes defined by ``PAP.Subject``. If one wants to query for
       instances of ``PAP.Person`` referred to by ``manager``, a type
       restriction is needed.

       To restrict ``my_node.manager`` to ``PAP.Person``:

        >>> Q.my_node.manager ["PAP.Person"]
        Q.my_node.manager ["PAP.Person"]

        >>> q1 = Q.OR (Q.my_node.manager, Q.my_node.owner) [Q.PAP.Person]
        >>> q2 = Q.my_node.OR (Q.manager, Q.owner) [Q.PAP.Person]

        >>> q1
        <_OR_ [Q.my_node.manager ["PAP.Person"], Q.my_node.owner ["PAP.Person"]]>

        >>> q2
        <_OR_ [Q.my_node.manager ["PAP.Person"], Q.my_node.owner ["PAP.Person"]]>

        To restrict ``my_node.manager`` or ``my_node.owner`` to ``PAP.Person``
        or ``PAP.Company``:

        >>> qh = Q.my_node.OR (Q.manager, Q.owner)
        >>> qh
        <_OR_ [Q.my_node.manager, Q.my_node.owner]>

        >>> qh.OR (Q [Q.PAP.Person], Q [Q.PAP.Company])
        <_OR_ [Q.my_node.manager ["PAP.Person"], Q.my_node.owner ["PAP.Person"], Q.my_node.manager ["PAP.Company"], Q.my_node.owner ["PAP.Company"]]>

        To restrict ``my_node.manager`` to ``PAP.Association`` or
        ``PAP.Company``:

        >>> q3 = Q.my_node.manager.OR (Q ["PAP.Association"], Q ["PAP.Company"])
        >>> q3
        <_OR_ [Q.my_node.manager ["PAP.Association"], Q.my_node.manager ["PAP.Company"]]>

        >>> q3 == 23
        <Filter_Or [Q.my_node.manager ["PAP.Association"] == 23, Q.my_node.manager ["PAP.Company"] == 23]>

        >>> q3.name == "ISAF"
        <Filter_Or [Q.my_node.manager ["PAP.Association"].name == 'ISAF', Q.my_node.manager ["PAP.Company"].name == 'ISAF']>

        To restrict ``manager`` to ``PAP.Company`` instances whose ``owner`` is
        an instance of ``PAP.Person``:

        >>> Q.manager [Q.PAP.Company].owner [Q.PAP.Person]
        Q.manager ["PAP.Company"].owner ["PAP.Person"]

        """

    _real_name       = "Base"

    @TFL.Meta.Once_Property
    def _re_type_restriction (self) :
        ### Once_Property to avoid circular imports
        import _MOM._Attr.Querier
        return MOM.Attr.Querier.regexp.type_restriction
    # end def _re_type_restriction

    def _getattr_transitive (self, name) :
        tr_pat = self._re_type_restriction
        if tr_pat.search (name) :
            h, typ, t  = tr_pat.split (name, 1, 2)
            result     = self.__super.__getattr__ (h) if h else self
            result     = result [typ]
            if t :
                result = getattr (result, t)
        else :
            result     = self.__super.__getattr__ (name)
        return result
    # end def _getattr_transitive

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return self._getattr_transitive (name)
    # end def __getattr__

Base = _MOM_Base_ # end class

Q = Base (Ignore_Exception = AttributeError)

@TFL.Override_Method (Base)
class _MOM_Get_ (Base._Get_) :
    """Query getter with support for E_Type restriction"""

    _real_name       = "_Get_"

    @property
    def RAW (self) :
        """Get raw value for attribute specified by getter `self`."""
        prefix, _, postfix = rsplit_hst (self._name, ".")
        Q = self.Q
        return Q.RAW._Get_Raw_ (Q, prefix = prefix, postfix = postfix)
    # end def RAW

    def __getitem__ (self, type_name) :
        """Restrict result of getter `self` to instances of E_Type with name
           `type_name`.
        """
        return self._E_Type_Restriction_ (self, type_name)
    # end def __getitem__

_Get_ = _MOM_Get_ # end class

@TFL.Add_Method (_Get_)
class _E_Type_Restriction_ (TFL.Q_Exp._Get_) :

    def __init__ (self, head_getter, type_name, tail_getter = None) :
        self.Q            = head_getter.Q
        self._head_getter = head_getter
        self._tail_getter = tail_getter
        if isinstance (type_name, _Get_) :
            type_name = type_name._name
        self._type_name   = type_name
    # end def __init__

    def predicate (self, obj) :
        Q  = self.Q
        tg = self._tail_getter
        try :
            result   = self._head_getter (obj)
            app_type = obj.E_Type.app_type
            E_Type   = app_type.entity_type (self._type_name)
            if E_Type is None :
                raise TypeError \
                    ( "App-type %s doesn't have E-Type with name %s"
                    % (app_type, type_name)
                    )
        except Q.Ignore_Exception as exc :
            result = Q.undef
        else :
            if isinstance (result, E_Type) :
                if tg is not None :
                    result = tg (result)
            elif isinstance (result, pyk.string_types + (dict, )) :
                result = Q.undef
            else :
                try :
                    _ = iter (result)
                except TypeError :
                    result = Q.undef
                else :
                    result = result.__class__ \
                        (v for v in result if isinstance (v, E_Type))
                    if tg is not None :
                        result = result.__class__ (tg (r) for r in result)
        return result
    # end def predicate

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        tg = self._tail_getter
        return self.__class__ \
            ( self._head_getter
            , self._type_name
            , getattr (tg if tg is not None else self.Q, name)
            )
    # end def __getattr__

    def __getitem__ (self, type_name) :
        return self.__class__ (self, type_name)
    # end def __getitem__

    def __repr__ (self) :
        result = """%r ["%s"]""" % (self._head_getter, self._type_name)
        tg     = self._tail_getter
        if tg is not None :
            result += repr (tg) [1:] ### skip leading `Q`
        return result
    # end def __repr__

# end class _E_Type_Restriction_

class Raw_Attr_Query (Base) :
    ### Syntactic sugar for creating Filter objects based on raw attribute
    ### queries.

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return self._Get_Raw_ (self, name)
    # end def __getattr__

# end class Raw_Attr_Query

Base.RAW = Raw_Attr_Query ()

@TFL.Add_New_Method (Raw_Attr_Query)
class _Get_Raw_ (TFL.Q_Exp._Get_) :
    """Query getter for raw values."""

    def __init__ (self, Q, postfix, prefix = "") :
        self.Q        = Q
        self._postfix = postfix
        self._prefix  = prefix
    # end def __init__

    def _getter (self, obj) :
        if self._prefix :
            obj = getattr (TFL.Getter, self._prefix) (obj)
        key = self._postfix
        if hasattr (obj, "raw_attr") and key in obj.attributes :
            return obj.raw_attr (key)
        else :
            getter = getattr (TFL.Getter, key)
            result = getter  (obj)
            if isinstance (obj, MOM.Entity) :
                result = pyk.text_type (result)
            return result
    # end def _getter

    @Once_Property
    def _name (self) :
        if self._prefix :
            return ".".join ((self._prefix, self._postfix))
        return self._postfix
    # end def _name

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return self.__class__ (self.Q, name, self._name)
    # end def __getattr__

    def __repr__ (self) :
        return "Q.RAW.%s" % (self._name, )
    # end def __repr__

# end class _Get_Raw_

### «text» ### start of documentation
__doc__ = r"""
This module implements a query expression language based on
:mod:`TFL.Q_Exp<_TFL.Q_Exp>`.

.. data:: Q

    It exports the query generator instance :obj:`Q` which is used to define
    symbolic query expressions that can be used for queries of the MOM object
    model. Unlike :obj:`TFL.Q<_TFL.Q_Exp.Q>`, :obj:`MOM.Q<_MOM.Q_Exp.Q>`
    ignores `AttributeError` exceptions.

One queries the object model by calling the
:meth:`~_MOM.E_Type_Manager.Entity.query` method of the appropriate etype
manager. Strict queries return only direct instances of the essential class in
question, but not instances of derived classes. Non-strict queries are
transitive, i.e., they return instances of the essential class in question and
all its descendants. For partial types, strict queries return nothing. By
default, queries are non-strict (transitive). Passing `strict = True` to a
query makes it strict.

The :meth:`~_MOM.E_Type_Manager.Entity.query` method returns a (lazy) query
result that is an instance of, or compatible to,
:class:`~_TFL.Q_Result._Q_Result_`.

One can pass Q-expressions to :meth:`~_MOM.E_Type_Manager.Entity.query` or to
the `attr`, `attrs`, `distinct`, `filter`, `group_by`, or `order_by` methods of
the query result. These Q-expressions can use all attributes stored in the
database and all query attributes, including reverse reference attributes; each
E_Type provides a property :attr:`~_MOM.Entity.Id_Entity.q_able` listing the
query-able attributes.

Simple example::

    # Query for all persons whose last name contains the string "tan"
    pq0 = scope.PAP.Person.query (Q.last_name.CONTAINS ("tan"))

    # Order the elements of the query result by last_name and first_name
    pq1 = pq0.order_by (Q.last_name, Q.first_name)

    # Limit the number of elements in query result to five
    pq2 = pq1.limit (5)

    # Materialize the elements of the query result
    persons = pq2.all ()

    # How many elements did the original query match?
    pql = pq0.count ()

In SQL terminology, some Q-expressions will trigger
automatic joins. For instance::

    phaq = scope.PAP.Person_has_Account.query \
        (Q.right.name.ENDSWITH ("@me.com")).distinct ()

Here, `Q.right` refers to an attribute of `PAP.Person_has_Account` but
`Q.right.name` refers to an attribute of `scope.Auth.Account`; for a SQL
database, a join is needed to evaluate the query.

Note, that normally the Q-expressions don't mention any types, tables, or
columns:

- Q-expressions are essential in that one doesn't need to know

  + which kind of database is used to store the object model;

  + which tables, if any, are storing which attributes;

  + exactly which set of types is involved in a query
    (for polymorphic queries).

  One and the same Q-expression can be thus be used to query different
  implementations of the same, or even slightly different, essential object
  model.

- The same Q-expression can be used to query for instances of different
  types or tables.

MOM supports polymorphic queries, possibly with
:ref:`type restriction<Type restrictions>`, like::

    scope.PAP.Subject_has_Property.query \
        ( Q.left [Q.PAP.Person].last_name.RAW == "Tanzer"
        , Q.right.desc == "office"
        )

In this example, ``PAP.Subject`` is an ancestor of ``PAP.Person``,
``PAP.Company``, and other classes; ``PAP.Property`` is an ancestor of
``PAP.Address``, ``PAP.Phone``, and other classes. ``Q.left [Q.PAP.Person]``
restricts the query result to those links where the ``left`` role refers to an
instance of ``PAP.Person``. Therefore, this query will return links of various
associations like ``PAP.Person_has_Account``, ``PAP.Person_has_Email``, or
``PAP.Person_has_Phone``!

For one specific object model implemented with a SQL database, the resulting
SQL query might look like::

    SELECT
      mom_id_entity.electric AS mom_id_entity_electric,
      mom_id_entity.last_cid AS mom_id_entity_last_cid,
      mom_id_entity.pid AS mom_id_entity_pid,
      mom_id_entity.type_name AS mom_id_entity_type_name,
      mom_id_entity.x_locked AS mom_id_entity_x_locked,
      pap_subject_has_phone.extension AS pap_subject_has_phone_extension,
      pap_subject_has_phone.pid AS pap_subject_has_phone_pid,
      pap_subject_has_property."desc" AS pap_subject_has_property_desc,
      pap_subject_has_property."left" AS pap_subject_has_property_left,
      pap_subject_has_property."right" AS pap_subject_has_property_right,
      pap_subject_has_property.pid AS pap_subject_has_property_pid
    FROM mom_id_entity
      JOIN pap_subject_has_property
        ON mom_id_entity.pid = pap_subject_has_property.pid
      LEFT OUTER JOIN pap_subject_has_phone
        ON pap_subject_has_property.pid = pap_subject_has_phone.pid
      LEFT OUTER JOIN pap_person
        ON pap_person.pid = pap_subject_has_property."left"
      LEFT OUTER JOIN pap_address
        ON pap_address.pid = pap_subject_has_property."right"
      LEFT OUTER JOIN pap_email
        ON pap_email.pid = pap_subject_has_property."right"
      LEFT OUTER JOIN pap_phone
        ON pap_phone.pid = pap_subject_has_property."right"
      LEFT OUTER JOIN pap_url
        ON pap_url.pid = pap_subject_has_property."right"
    WHERE pap_person.__raw_last_name = :__raw_last_name_1
       AND (  pap_address."desc" = :desc_1
           OR pap_email."desc" = :desc_2
           OR pap_phone."desc" = :desc_3
           OR pap_url."desc" = :desc_4
           )

with the parameters::

    __raw_last_name_1    : 'Tanzer'
    desc_1               : 'office'
    desc_2               : 'office'
    desc_3               : 'office'
    desc_4               : 'office'

Adding a type restriction for ``Q.right``, like::

    scope.PAP.Subject_has_Property.query \
        ( Q.left  [Q.PAP.Legal_Entity]
        , Q.right [Q.PAP.Phone].cc == "43"
        )

reduces the number of joins for the right link role::

    SELECT
      mom_id_entity.electric AS mom_id_entity_electric,
      mom_id_entity.last_cid AS mom_id_entity_last_cid,
      mom_id_entity.pid AS mom_id_entity_pid,
      mom_id_entity.type_name AS mom_id_entity_type_name,
      mom_id_entity.x_locked AS mom_id_entity_x_locked,
      pap_subject_has_phone.extension AS pap_subject_has_phone_extension,
      pap_subject_has_phone.pid AS pap_subject_has_phone_pid,
      pap_subject_has_property."desc" AS pap_subject_has_property_desc,
      pap_subject_has_property."left" AS pap_subject_has_property_left,
      pap_subject_has_property."right" AS pap_subject_has_property_right,
      pap_subject_has_property.pid AS pap_subject_has_property_pid
    FROM mom_id_entity
      JOIN pap_subject_has_property
        ON mom_id_entity.pid = pap_subject_has_property.pid
      LEFT OUTER JOIN pap_subject_has_phone
        ON pap_subject_has_property.pid = pap_subject_has_phone.pid
      LEFT OUTER JOIN pap_association AS pap_association__1
        ON pap_association__1.pid = pap_subject_has_property."left"
      LEFT OUTER JOIN pap_company AS pap_company__1
        ON pap_company__1.pid = pap_subject_has_property."left"
      LEFT OUTER JOIN pap_phone
        ON pap_phone.pid = pap_subject_has_property."right"
    WHERE (pap_association__1.pid IS NOT NULL
       OR pap_company__1.pid IS NOT NULL)
       AND pap_phone.cc = :cc_1

In a different application that doesn't import ``PAP.Association``,
exactly the same  query would result in **one less join**
(because there wouldn't be a table ``pap_association``).

"""

if __name__ != "__main__" :
    MOM._Export ("Q")
    MOM._Export_Module ()
### __END__ MOM.Q_Exp
