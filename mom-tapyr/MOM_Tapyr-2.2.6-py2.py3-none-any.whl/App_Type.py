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
#    MOM.App_Type
#
# Purpose
#    Encapsulate information about a specific application type
#
# Revision Dates
#    16-Oct-2009 (CT) Creation
#    18-Oct-2009 (CT) Creation continued
#    18-Nov-2009 (CT) `_App_Type_` and `_App_Type_D_` factored
#    23-Nov-2009 (CT) `finalized` added and used to guard `add_type`
#    23-Nov-2009 (CT) Documentation added
#    30-Dec-2009 (CT) s/Package_NS/PNS/
#    14-Jan-2010 (CT) `PNS_Aliases` added
#     4-Mar-2010 (CT) `delete_database` added
#    24-Jun-2010 (CT) `Url` added
#    24-Jun-2010 (CT) `db_sig` and `db_version_hash` added
#    30-Jun-2010 (CT) `Once_Property` for `Version` added
#    22-Dec-2010 (CT) `etypes_by_pns` addded
#    18-Nov-2011 (CT) Add `attribute_types`
#    26-Jun-2012 (CT) Add `PNS_Aliases_R`
#     9-Apr-2013 (CT) Add `DBW.db_sig` to `db_sig`
#    10-May-2013 (CT) Add `all_attribute_types`
#     5-Jun-2013 (CT) Add `surrogate_map`
#     7-Jun-2013 (CT) Add `surrogate_t_map`
#    13-Jun-2013 (CT) Move `PNS_Aliases`, `PNS_Aliases_R` to `MOM.Entity`
#    13-Jun-2013 (CT) Add `PNS_Set`
#    23-Aug-2013 (CT) Add guard for `fqn != qn` to `add_type`
#    12-Oct-2014 (CT) Use `TFL.user_config.sha` instead of home-grown code
#    17-Oct-2014 (CT) Change `db_sig` to use a dict, not tuple, of E_Types
#    12-Oct-2015 (CT) Apply `pyk.decoded` to `result` of `db_version_hash`
#    ««revision-date»»···
#--

from   _MOM                  import MOM
from   _TFL                  import TFL
from   _TFL.pyk              import pyk

import _MOM._EMS.Backends

import _TFL.multimap
import _TFL.Ordered_Set
import _TFL.User_Config
import _TFL._Meta.Object
import _TFL._Meta.Once_Property

@pyk.adapt__str__
class _App_Type_ (TFL.Meta.Object) :
    """Encapsulate information about a specific application type."""

    def add_init_callback (self, * callbacks) :
        """Add all `callbacks` to `init_callback`. These
           callbacks are executed whenever a :class:`~_MOM.Scope.Scope` is
           created (the new scope is passed as the single argument to each
           callback).
        """
        self.init_callback.extend (callbacks)
    # end def add_init_callback

    def add_kill_callback (self, * callbacks) :
        """Add all `callbacks` to `kill_callback`. These
           callbacks` are executed whenever a :class:`~_MOM.Scope.Scope` is
           destroyed (the scope to be destroyed is passed as the single
           argument to each callback).
        """
        self.kill_callback.extend (callbacks)
    # end def add_kill_callback

    @staticmethod
    def instance (name) :
        return App_Type.Table [name]
    # end def instance

    def run_init_callbacks (self, scope) :
        for c in self.init_callback :
            c (scope)
    # end def run_init_callbacks

    def run_kill_callbacks (self, scope) :
        for c in self.kill_callback :
            c (scope)
    # end def run_kill_callbacks

    def Url (self, db_url) :
        if isinstance (db_url, pyk.string_types) :
            _, _, DBS = MOM.EMS.Backends.get (db_url)
            return DBS.Url (db_url, self.ANS)
        return db_url
    # end def Url

    @TFL.Meta.Once_Property
    def Version (self) :
        return self.ANS.Version
    # end def Version

    def __getitem__ (self, name) :
        return self.etypes [name]
    # end def __getitem__

    def __repr__ (self) :
        return "%s (%r, %s)" % \
            ( self.__class__.__name__
            , self.name, self.ANS._Package_Namespace__qname
            )
    # end def __repr__

    def __str__ (self) :
        return self.name
    # end def __str__

# end class _App_Type_

class _App_Type_D_ (_App_Type_) :
    """App_Type derived for a specific combination of `EMS` and `DBW`"""

    @TFL.Meta.Once_Property
    def attribute_types (self) :
        """List of all attribute types used by the etypes of the application."""
        result = set ()
        for T in self._T_Extension :
            if not T.is_partial :
                for ak in T.edit_attr :
                    result.add (ak.attr)
        return sorted (result, key = TFL.Sorted_By ("typ", "name"))
    # end def attribute_types

    @TFL.Meta.Once_Property
    def all_attribute_types (self) :
        """List of all attribute types used by the etypes of the application."""
        result = set ()
        for T in self._T_Extension :
            if not T.is_partial :
                for ak in pyk.itervalues (T.attributes) :
                    result.add (ak.attr)
        return sorted (result, key = TFL.Sorted_By ("typ", "name"))
    # end def all_attribute_types

    @TFL.Meta.Once_Property
    def db_version_hash (self) :
        sha    = TFL.user_config.sha
        result = sha (self.db_sig).b64digest (strip = True)
        return pyk.decoded (result)
    # end def db_version_hash

    @TFL.Meta.Once_Property
    def db_sig (self) :
        return \
            ( self.DBW.db_sig
            , dict
                (  (T.type_name, T.db_sig)
                for T in self._T_Extension if T.relevant_root
                )
            )
    # end def db_sig

    @property
    def PNS_Aliases (self) :
        return MOM.Entity.PNS_Aliases
    # end def PNS_Aliases

    @property
    def PNS_Aliases_R (self) :
        return MOM.Entity.PNS_Aliases_R
    # end def PNS_Aliases_R

    @property
    def Root_Type (self) :
        if self.Root_Type_Name :
            return self.etypes [self.Root_Type_Name]
    # end def Root_Type

    def __init__ (self, parent, EMS, DBW) :
        assert parent
        self.name             = "__".join \
            ((parent.name, EMS.type_name, DBW.type_name))
        self.ANS              = parent.ANS
        self.Root_Type_Name   = parent.Root_Type_Name
        self.EMS              = EMS
        self.DBW              = DBW
        self.etypes           = {}
        self.etypes_by_pns    = TFL.mm_list ()
        self._T_Extension     = []
        self.derived          = None
        self.parent           = parent
        self.init_callback    = TFL.Ordered_Set ()
        self.kill_callback    = TFL.Ordered_Set ()
        self.PNS_Map          = parent.PNS_Map
        self.PNS_Set          = parent.PNS_Set
        self.surrogate_map    = {}
        self.surrogate_t_map  = {}
        self.finalized        = False
        MOM.Entity.m_setup_etypes (self)
        self.finalized        = True
    # end def __init__

    def add_type (self, etype) :
        assert not self.finalized
        pns = etype.PNS
        qn  = etype.pns_name
        fqn = pns._Package_Namespace__qname
        self.etypes [etype.type_name]          = \
            self.etypes [etype.type_name_fq]   = etype
        self.PNS_Map [qn] = self.PNS_Map [fqn] = self.PNS_Set [qn] = pns
        self.etypes_by_pns [ qn].append (etype)
        if fqn != qn :
            self.etypes_by_pns [fqn].append (etype)
        self._T_Extension.append (etype)
    # end def add_type

    def delete_database (self, db_url) :
        if db_url :
            url = self.Url (db_url)
            self.DBW.delete_database (url)
    # end def delete_database

    def entity_type (self, entity) :
        """Returns app-type specific type of `entity`."""
        if isinstance (entity, pyk.string_types) :
            name = entity
        else :
            name = entity.Essence.type_name
        result   = self.etypes.get (name)
        return result
    # end def entity_type

    def run_init_callbacks (self, scope) :
        for c in self.parent.init_callback :
            c (scope)
        self.__super.run_init_callbacks (scope)
    # end def run_init_callbacks

    def run_kill_callbacks (self, scope) :
        self.__super.run_kill_callbacks (scope)
        for c in self.parent.kill_callback :
            c (scope)
    # end def run_kill_callbacks

# end class _App_Type_D_

class App_Type (_App_Type_) :
    """Encapsulate information about a specific application type.

       `MOM.App_Type` defines the characteristics of a specific
       application. It encapsulates information about the essential
       object model of the application.

       Each `App_Type` is instantiated with the attributes:

       .. attribute:: name

         Name of the app-type.

       .. attribute:: ANS

         Specifies the package namespace of the application (Application
         Name Space).

       .. attribute:: Root_Type_Name

         Specifies the name of the `root type` of the application, if
         any. If there is a root type, each scope created has its own
         specific root object which is an instance of the root type.

       `App_Type` provides the methods:

       .. automethod:: add_init_callback
       .. automethod:: add_kill_callback
       .. automethod:: Derived
    """

    Table            = {}

    DBW              = None
    EMS              = None
    etypes           = None
    parent           = None
    _T_Extension     = None

    def __init__ (self, name, ANS, Root_Type_Name = None) :
        assert bool (name)
        assert name not in self.Table
        self.Table [name]   = self
        self.name           = name
        self.ANS            = ANS
        self.Root_Type_Name = Root_Type_Name
        self.derived        = {}
        self.init_callback  = TFL.Ordered_Set ()
        self.kill_callback  = TFL.Ordered_Set ()
        self.PNS_Map        = {}
        self.PNS_Set        = {}
    # end def __init__

    def Derived (self, EMS, DBW) :
        """Return an :class:`_App_Type_D_` derived for a specific
           combination of `EMS` and `DBW`.
        """
        if (EMS, DBW) in self.derived :
            result = self.derived [EMS, DBW]
        else :
            result = self.derived [EMS, DBW] = _App_Type_D_ (self, EMS, DBW)
        return result
    # end def Derived

# end class App_Type

### «text» ### start of documentation
__doc__ = """


.. class:: _App_Type_D_

    A derived `App_Type` adds a specific `entity manager strategy`
    `EMS` and a specific data base wrapper `DBW` to a parent
    `App_Type`.

    For each essential object and link type of an application, a
    derived `App_Type` holds an app-type specifc entity type (short
    `etype`) derived from the essential type. For some `DBWs`, the
    etype might contain additional properties injected by the `DBW`.

    As the etypes are automatically created, when a derived `App_Type`
    is instantiated, all essential classes must be defined by then.
    The current implementation does not allow defining essential
    object or link classes after the creation of the app-type.

    Derived `App_Types` provide the additonal properties:

    .. attribute:: Root_Type

      The entity type of the root object, if any.

    .. attribute:: attribute_types

      List of all attribute types used by the etypes of the application.

    .. attribute:: db_sig

      A tuple of all the :attr:`db_sig<MOM.Meta.M_E_Type.db_sig>`
      values of all relevant etypes of the application.

    .. attribute:: db_version_hash

      Hash value of the app-type's :attr:`db_sig`. Some `DBWs` use
      the `db_version_hash` to identify incompatibilities between the
      application version and the database version.

          The `db_version_hash` is implemented as a SHA checksum.

    .. attribute:: etypes

      Maps names of essential associations and objects to the
      appropriate app-type specific classes.

          For each essential class defined for a `App_Type`, the meta
          machinery automatically creates an app-type specific class that
          combines essential properties and app-type specific properties
          of the class in question.

    .. automethod:: entity_type

"""

if __name__ != "__main__" :
    MOM._Export ("*")
### __END__ MOM.App_Type
