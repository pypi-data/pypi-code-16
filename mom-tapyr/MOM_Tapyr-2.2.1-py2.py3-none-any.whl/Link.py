# -*- coding: utf-8 -*-
# Copyright (C) 2009-2015 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package _MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Link
#
# Purpose
#    Root class for link-types of MOM meta object model
#
# Revision Dates
#    22-Oct-2009 (CT) Creation (factored from TOM.Link)
#     4-Nov-2009 (CT) `Link2` added
#    20-Nov-2009 (CT) `Link3` and `Link2_Ordered` added
#    20-Nov-2009 (CT) Documentation added
#    26-Nov-2009 (CT) `Role_Cacher` added
#    26-Nov-2009 (CT) `_init_epk` and `destroy` redefined to handle
#                     `auto_cache_roles`
#    27-Nov-2009 (CT) `Role_Cacher.setup` changed to store `other_role`
#                     instead of `other_role_name`
#    28-Nov-2009 (CT) `is_partial = True` added to all classes
#     3-Dec-2009 (CT) `Link3` and `Link2_Ordered` derived from `Link` instead
#                     of from `Link2` (and `_Attributes` moved from `Link2`
#                     to `Link`)
#    22-Dec-2009 (CT) `Link2_Ordered` changed to use `A_Int` for `seq_no` and
#                     directly derived from `Link2`
#    18-Jan-2010 (CT) `Role_Cacher_1` factored, `Role_Cacher_n` added
#     8-Feb-2010 (CT) `Link` changed to redefine `_destroy`, not `destroy`
#    18-Feb-2010 (CT) `Link1` added, `_MOM_Link_n_` factored
#    19-Feb-2010 (CT) `Link_Cacher` added, `_Cacher_` factored
#    19-Feb-2010 (CT) `Role_Cacher.setup` changed to create `A_Cached_Role`
#                     for `other_type` (factored in here from
#                     `M_Link_n._m_setup_auto_cache_role`)
#    19-Feb-2010 (CT) Argument `attr_class` added to `_setup_attr`
#    25-Feb-2010 (CT) Redefine `_finish__init__` instead of `_init_epk`
#     4-Mar-2010 (CT) `_Cacher_.cr_attr` added
#    22-Apr-2010 (CT) `_rename` redefined to honor `auto_cache_roles`
#     5-May-2010 (CT) `Link_Cacher._auto_attr_name` changed to call `lower`
#    11-May-2010 (CT) `_Cacher_.grn` added
#     4-Sep-2010 (CT) Use `cache.discard` instead of `cache.remove`
#    29-Mar-2011 (CT) `Link1.left` redefined to mixin `Init_Only_Mixin`
#    22-Sep-2011 (CT) s/Class/P_Type/ for _A_Id_Entity_ attributes
#    23-Mar-2012 (CT) Add `copy`, `copy_args`, and `link_type_name`
#    24-Mar-2012 (CT) Add `__repr__` to `_Cacher_`
#    29-Mar-2012 (CT) Change `_Cacher_._setup_attr` to not redefine `cr_attr`
#    18-Jun-2012 (CT) Add `_Reload_Mixin_` for `Link1`, `Link2`, `Link3`
#    26-Jun-2012 (CT) Add `if cache` to `Role_Cacher_n.__call__`
#     1-Aug-2012 (CT) Add `_Link[123]_Destroyed_Mixin_`
#     4-Aug-2012 (CT) Guard `cache.remove` in `Link_Cacher_n.__call__`
#    13-Sep-2012 (CT) Add `_suffixed`
#    14-Sep-2012 (CT) Add `cr_name` to `Link_Cacher`, `Role_Cacher`
#    27-Sep-2012 (CT) Remove un-implemented `Link_AB` from docstring
#    29-Jan-2013 (MG) Add cacher object to auto created obbject
#    15-May-2013 (CT) Remove `Link2_Ordered`
#    15-May-2013 (CT) Remove `_Cacher_` and role- and link-cacher children
#    15-May-2013 (CT) Rename `auto_cache` to `auto_rev_ref`
#    17-Jun-2013 (CT) Add `_MOM_Link_n_` to `_Export`
#    14-Sep-2015 (CT) Add `_real_name` for `_Link_n_`
#    16-Dec-2015 (CT) Add `Link1._UI_Spec_Defaults`
#    ««revision-date»»···
#--

from   _TFL      import TFL
from   _MOM      import MOM

from   _MOM._Attr.Type import *
from   _MOM._Attr      import Attr
from   _MOM._Pred      import Pred

import  _MOM._Meta.M_Link

import _MOM.Entity

_Ancestor_Essence = MOM.Id_Entity

class _MOM_Link_ \
          (TFL.Meta.BaM (_Ancestor_Essence, metaclass = MOM.Meta.M_Link)) :
    """Root class for link-types of MOM meta object model."""

    _real_name            = "Link"
    entity_kind           = "link"
    is_partial            = True
    is_synthetic          = False

    class _Attributes (_Ancestor_Essence._Attributes) :

        class left (_A_Link_Role_Left_, A_Link_Role_EB) :
            """Left role of association. Override to define `role_type`, ..."""

        # end class left

    # end class _Attributes

    @property
    def roles (self) :
        """Link roles as tuple of cooked values (subset of :attr:`epk`)."""
        return self.epk [:self.number_of_roles]
    # end def roles

    def _finish__init__ (self) :
        self.__super._finish__init__ ()
        for role_cacher in self.auto_cache_roles :
            role_cacher (self, no_value = False)
    # end def

    def _destroy (self) :
        for role_cacher in self.auto_cache_roles :
            role_cacher (self, no_value = True)
        self.__super._destroy ()
    # end def _destroy

    def _rename (self, new_epk, pkas_raw, pkas_ckd) :
        result = self.__super._rename (new_epk, pkas_raw, pkas_ckd)
        for role_cacher in self.auto_cache_roles :
            role_cacher (self, no_value = False)
        return result
    # end def _rename

Link = _MOM_Link_ # end class

_Ancestor_Essence = Link

class Link1 (TFL.Meta.BaM (_Ancestor_Essence, metaclass = MOM.Meta.M_Link1)) :
    """Common base class for essential unary links of MOM"""

    is_partial            = True

    _UI_Spec_Defaults     = dict \
        ( show_in_admin   = True
        )

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :

            Kind_Mixins   = (Attr.Init_Only_Mixin, )

        # end class left

    # end class _Attributes

# end class Link1

_Ancestor_Essence = Link

class _MOM_Link_n_ \
          (TFL.Meta.BaM (_Ancestor_Essence, metaclass = MOM.Meta.M_Link_n)) :
    """Root class for link-types of MOM meta object model with more than 1 role."""

    is_partial            = True
    _real_name            = "_Link_n_"

    class _Attributes (_Ancestor_Essence._Attributes) :

        class right (_A_Link_Role_Right_, A_Link_Role_EB) :
            """Right role of association. Override to define `role_type`, ..."""

        # end class right

    # end class _Attributes

_Link_n_ = _MOM_Link_n_ # end class

_Ancestor_Essence = _Link_n_

class Link2 (TFL.Meta.BaM (_Ancestor_Essence, metaclass = MOM.Meta.M_Link2)) :
    """Common base class for essential binary links of MOM."""

    is_partial            = True

# end class Link2

_Ancestor_Essence = _Link_n_

class Link3 (TFL.Meta.BaM (_Ancestor_Essence, metaclass = MOM.Meta.M_Link3)) :
    """Common base class for essential ternary links of MOM."""

    is_partial            = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        class middle (_A_Link_Role_Middle_, A_Link_Role_EB) :
            """Middle role of association. Override to define `role_type`, ..."""

        # end class middle

    # end class _Attributes

# end class Link3

@TFL.Add_To_Class ("_Destroyed_Mixin_", Link1)
class _Link1_Destroyed_Mixin_ \
          ( TFL.Meta.BaM
              ( MOM._Id_Entity_Destroyed_Mixin_
              , metaclass = MOM.Meta.M_E_Type_Link1_Destroyed
              )
          ) :
    """Mixin triggering an exception on any attribute access to a
       destroyed Link1.
    """

# end class _Link1_Destroyed_Mixin_

@TFL.Add_To_Class ("_Destroyed_Mixin_", Link2)
class _Link2_Destroyed_Mixin_ \
          ( TFL.Meta.BaM
              ( MOM._Id_Entity_Destroyed_Mixin_
              , metaclass = MOM.Meta.M_E_Type_Link2_Destroyed
              )
          ) :
    """Mixin triggering an exception on any attribute access to a
       destroyed Link2.
    """

# end class _Link2_Destroyed_Mixin_

@TFL.Add_To_Class ("_Destroyed_Mixin_", Link3)
class _Link3_Destroyed_Mixin_ \
          ( TFL.Meta.BaM
              ( MOM._Id_Entity_Destroyed_Mixin_
              , metaclass = MOM.Meta.M_E_Type_Link3_Destroyed
              )
          ) :
    """Mixin triggering an exception on any attribute access to a
       destroyed Link3.
    """

# end class _Link3_Destroyed_Mixin_

@TFL.Add_To_Class ("_Reload_Mixin_", Link1)
class _Link1_Reload_Mixin_ \
          ( TFL.Meta.BaM
              ( MOM._Id_Entity_Reload_Mixin_
              , metaclass = MOM.Meta.M_E_Type_Link1_Reload
              )
          ) :
    """Mixin triggering a reload from the database on any attribute access."""

# end class _Link1_Reload_Mixin_

@TFL.Add_To_Class ("_Reload_Mixin_", Link2)
class _Link2_Reload_Mixin_ \
          ( TFL.Meta.BaM
              ( MOM._Id_Entity_Reload_Mixin_
              , metaclass = MOM.Meta.M_E_Type_Link2_Reload
              )
          ) :
    """Mixin triggering a reload from the database on any attribute access."""

# end class _Link2_Reload_Mixin_

@TFL.Add_To_Class ("_Reload_Mixin_", Link3)
class _Link3_Reload_Mixin_ \
          ( TFL.Meta.BaM
              ( MOM._Id_Entity_Reload_Mixin_
              , metaclass = MOM.Meta.M_E_Type_Link3_Reload
              )
          ) :
    """Mixin triggering a reload from the database on any attribute access."""

# end class _Link3_Reload_Mixin_

### «text» ### start of documentation
Link.__doc_attr_head__ = """
    `MOM.Link` provides the framework for defining essential
    associations. It is based on :class:`~_MOM.Entity.Id_Entity`.

    An association models the relationship between two or
    more objects or links of essential classes. An association manages the
    set of links between the entities of the associated classes.
    Conceptually, each link is an independent entity.

    The class `Link` simultaneously models two concepts:

    - The class `Link` itself models the association, i.e., the
      collection of all links.

      The behavior of the association is provided by the methods and
      properties of the link manager
      :class:`E_Type_Manager<_MOM.E_Type_Manager.Link>`.

    - Each instance of `Link` models one specific link of the association.

    Each essential association is characterized by:

    - `arity`_

    - `roles`_

    - `multiplicity`_

    .. _`arity`:

    **Arity**

    Arity defines how many objects one link comprises. A unary link relates
    the (attributes of the) link to one object. A binary association relates
    pairs of objects to each other, a ternary association relates triples of
    objects to each other, and so on.

    For each arity, a separate subclass exists, e.g., :class:`Link2`,
    :class:`Link3`, etc. Each arity-specific subclass has its own
    arity-specific metaclass, e.g., :class:`M_Link3` defines the behavior of
    :class:`Link3`.

    An essential association is modelled by a class that inherits from the
    proper arity-specific descendent of :class:`Link_EB`.

    * :class:`Link1`

    * :class:`Link2`

    * :class:`Link3`

    .. _`roles`:

    **Roles**

    Each object participating in a link of an association plays a specific
    `role`. A role is characterized by:

    * Role type: the type of essential object expected.

    * Role name (default `role_type.type_base_name.lower ()`).

      - If an association links objects of the same types in different
        roles to each other, at least one, preferably all of these roles
        need a unique role name that's different from the default role
        name.

    * Generic role name (e.g., `left` or `right`).

    * Role abbreviation (e.g., `l` or `r`).

    * Multiplicity constraint, if any.

    * Non-essential properties:

      - `link_ref_attr_name` (see `link-ref-attr-name`_)

      - `auto_rev_ref` (see `auto-rev-ref`_)

    Each role of a specific association is defined by a link-role attribute
    named by the generic role name. For a specific association, the link-role
    attribute

      * Must define :attr:`role_type` (unless that's already inherited).

      * May define :attr:`role_name`, multiplicity constraints
        (:attr:`max_links`) or any non-essential property of the role.

    For instance::

        class Person_works_for_Company (Link2) :

            class _Attributes (Link2._Attributes) :

                class left (Link2._Attributes.left) :
                    role_type     = Person
                    role_name     = "employee"
                    auto_rev_ref  = True
                    max_links     = 1 ### Danger, Will Robinson
                # end class left

                class right (Link2._Attributes.right) :
                    role_type     = Company
                    role_name     = "employer"
                # end class right

            # end class _Attributes

    .. _`multiplicity`:

    **Multiplicity**

    Multiplicity restricts how many links can exist for a single object
    in a specific role. Constraints on multiplicity frequently change over
    the lifetime of a software application.

    Common multiplicities (of binary associations) are:

    - 1 <--> 1

    - 1 <--> n

    - n <--> m

    Associations with at least one role with multiplicity 1 could be
    implemented by an attribute of the respective object instead of an
    association. Any change of requirements might invalidate that
    implementation, though.

    Simple multiplicity constraints are implemented by defining
    `max_links` for the appropriate role. In this case, the `Link` class
    will enforce the constraint.

    .. _`link-ref-attr-name`:

    **Link-ref-attr-name**

    For each link-role, the metaclass of the link automatically creates a query
    attribute of type `A_Link_Ref_List` for the role-type that returns the
    links in which the object is referred to by that link-role.

    By default, the name of `A_Link_Ref_List` attributes is:

    - for :class:`Link1`, the `type_base_name` in lower case

    - for :class:`Link2`, the `role_name` of the other link-role

    - for :class:`Link3`, the `role_name` of the other link-roles joined
      by "__"

    This default can be overriden by defining the property `link_ref_attr_name`
    for the link-role; setting `link_ref_attr_name` to `Undef()` inhibits the
    creation of the `A_Link_Ref_List` attribute.

    Unless `link_ref_suffix` is set to `None` for the link-role, the name of
    the `A_Link_Ref_List` is then pluralized, assuming English rules for
    pluralization.

    .. _`auto-rev-ref`:

    **Auto-Rev-Ref**

    By specifying `auto_rev_ref` for one of the `roles` of an entity-based
    association, an attribute referring to the objects linked via this
    association is automagically added to another role of the association.

    `auto_rev_ref` can be set to one of the values:

    - `True`. This only works for binary associations.As it is the simplest
      case, it should be preferred over the other possibilities, if possible.

    - A string specifying the name of the auto-rev-ref attribute.

"""

__doc__ = """

"""

future_features = """

DFC-Synthesis
-------------

Some object models allow recursive structures of the form:

- A container-like class `C` inherits from class `X`. `C` thus is
  substitutable for `X` and can participate in all associations
  defined for `X`.

- An association `X_in_C` that defines a container-like association
  with the multiplicity constraint that each instance of `X` is
  restricted to a single link to `C`.

In many such models, the instances of `X` linked to a specific
container `c` should reflect the links `c` itself participates in. To
avoid numerous redundant links, the module :mod:`~_MOM.DFC_Link`
provides classes that allow the automatic synthesis of links derived
from a container association.

DFC-synthesis is specified for the association that needs synthetic
`DFC_Links` by defining the property `dfc_synthesizer` (which must be
an instance of a subclass of :class:`~_MOM.DFC_Link.DFC_Synthesizer`)
for the role related to `X`.

For instance, given `C`, `X`, and `X_in_C` as described above,
DFC-synthesis for an association `X_has_P` would be defined like::

    class X_has_P (Link2) :

        class _Attributes (Link2._Attributes) :

            class left (Link2._Attributes.left) :
                role_type       = X
                dfc_synthesizer = MOM.DFC_Synthesizer_LL (X_in_C)
            # end class left

            class right (Link2._Attributes.right) :
                role_type       = P
            # end class right

        # end class _Attributes

"""

if __name__ != "__main__" :
    MOM._Export ("*", "_Link_n_")
### __END__ MOM.Link
