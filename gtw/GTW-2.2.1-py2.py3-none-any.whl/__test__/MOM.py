# -*- coding: utf-8 -*-
# Copyright (C) 2009-2017 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.__test__.MOM
#
# Purpose
#    Test for MOM meta object model
#
# Revision Dates
#    18-Oct-2009 (CT) Creation
#     4-Nov-2009 (CT) Creation continued
#     4-Nov-2009 (MG) `Beaver` and `Otter` added
#    23-Nov-2009 (CT) Creation continued..
#    24-Nov-2009 (CT) Creation continued...
#    25-Nov-2009 (CT) Creation continued....
#    27-Nov-2009 (CT) Creation continued.....
#    27-Nov-2009 (MG) Order of test cases changed, use `list` operator in
#                     some tests
#     4-Dec-2009 (MG) Tests adopted to use real database back end
#    14-Jan-2010 (CT) `ui_name` added to some attributes
#    18-Jan-2010 (MG) Tests fixed (`Invalid_Attribute` now has a different
#                     error message)
#    21-Jan-2010 (CT) `Primary_Optional` added
#    29-Jan-2010 (MG) Tests for scope rollback added/enhanced
#    29-Jan-2010 (MG) Tests for pid_from_lid/pid_as_lid/obj.lid/ added
#     6-Feb-2010 (MG) Use `t4` for new `auto_up_depends` test instance of
#                     `t1` (because all other traps are are already destroyed)
#     8-Feb-2010 (CT) Doctest for `t4.up_ex` corrected
#    14-Feb-2010 (MG) Fixed doctest after fixing `Entity._record_iter` (which
#                     introducted a new change object)
#    18-Feb-2010 (CT) `Rodent_is_sick` added to test unary links
#    19-Feb-2010 (MG) Test for auto cached links added
#    24-Feb-2010 (CT) s/Lifetime/Date_Interval/
#    17-May-2010 (CT) Test for `scope.migrate` added
#    17-Aug-2010 (CT) Use A_Float instead of A_Decimal to avoid sqlite warning
#     1-Sep-2010 (CT) Tests for `Q.attr`, `Q.attrs`, and `Q.set` added
#    28-Sep-2010 (CT) Adapted to change of `epk_raw`
#    20-Dec-2010 (CT) Python 2.7 compatibility
#     8-Feb-2011 (CT) s/Required/Necessary/, s/Mandatory/Required/
#    18-Nov-2011 (CT) Add `formatted1` to get rid of `u` prefixes
#    15-Apr-2012 (CT) Adapt to changes of `MOM.Error`
#    16-Apr-2012 (CT) Adapt to more changes of `MOM.Error`
#    14-May-2012 (CT) Add `Supertrap.weights` to test `A_Float_Interval`
#    14-May-2012 (CT) Factor function `show_children` to module `MOM.inspect`
#    14-May-2012 (CT) Remove prefix `u` from strings,
#                     import `unicode_literals` from `__future__` instead
#     8-Jun-2012 (CT) Add test for `query_changes` of `type_name`
#     3-Aug-2012 (CT) Use `Ref_Req_Map`, not `link_map`
#    11-Oct-2012 (CT) Add test for `signified`, import `MOM.Attr.Position`
#    12-Oct-2012 (CT) Adapt to repr change of `An_Entity`
#     6-Dec-2012 (CT) Add attributes `creation`, ...
#    23-Jan-2013 (MG) Use `last_change` instead of `max_cid` in some tests
#    25-Feb-2013 (CT) Replace `up_ex_q.auto_up_depends` by `query_preconditions`
#                     add tests for `up_ex_q`
#    17-Jun-2014 (RS) `Date_Time_Delta`, `Int_Interval`, `Int_Interval_C`
#    23-Jun-2014 (RS) Add `reaction_time_range` to test `Int_Interval_C`
#    22-Feb-2016 (CT) Add test for `height`, an attribute with unit
#    24-Feb-2017 (CT) Import `MOM.Inspect`, not `MOM.inspect`
#    ««revision-date»»···
#--

from   __future__  import print_function, unicode_literals

from   _MOM.import_MOM            import *
from   _MOM.import_MOM            import _A_Unit_
from   _MOM._Attr.Date_Interval   import *
from   _MOM._Attr.Number_Interval import A_Float_Interval
from   _MOM._Attr.Number_Interval import A_Int_Interval_C
from   _MOM._Attr.Date_Time_Delta import A_Date_Time_Delta

from   _MOM.Inspect               import \
    show_children, show_ref_map, show_ref_maps
from   _MOM.Product_Version       import Product_Version, IV_Number
from   _TFL.Package_Namespace     import Derived_Package_Namespace
from   _TFL                       import sos
from   _TFL.portable_repr         import portable_repr
from   _TFL.pyk                   import pyk

import _MOM._Attr.Position

def prepr (* args) :
    print (* (portable_repr (a) for a in args))

BMT = Derived_Package_Namespace (parent = MOM, name = "_BMT")

Version = Product_Version \
    ( productid           = "Better Mouse Trap"
    , productnick         = "BMT"
    , productdesc         = "Example application for MOM meta object model"
    , date                = "18-Dec-2009"
    , major               = 0
    , minor               = 5
    , patchlevel          = 42
    , author              = "Christian Tanzer, Martin Glück"
    , copyright_start     = 2009
    , db_version          = IV_Number
        ( "db_version"
        , ("Better Mouse Trap", )
        , ("Better Mouse Trap", )
        , program_version = 1
        , comp_min        = 0
        , db_extension    = ".bmt"
        )
    , script_api_version  = IV_Number
        ( "script_api_version"
        , ("Better Mouse Trap", )
        , ("Example Client 1", "Example Client 2")
        , program_version = 1
        , comp_min        = 0
        )
    )

class Named_Object (MOM.Object) :
    """Common base class for essential named objects of MOM."""

    is_partial            = True

    class _Attributes (MOM.Object._Attributes) :

        class name (A_Name) :
            """Unique name of the object."""

            kind        = Attr.Primary

        # end class name

    # end class _Attributes

# end class Named_Object

_Ancestor_Essence = MOM.Object

class Location (_Ancestor_Essence) :
    """Model a location of the Better Mouse Trap application."""

    PNS = BMT

    class _Attributes (_Ancestor_Essence._Attributes) :

        class lon (A_Float) :
            """Longitude """

            kind       = Attr.Primary
            rank       = 1
            min_value  = -180.0
            max_value  = +180.0
            ui_name    = "Longitude"

        # end class lon

        class lat (A_Float) :
            """Latitude"""

            kind       = Attr.Primary
            rank       = 2
            min_value  = -90.0
            max_value  = +90.0
            ui_name    = "Latitude"

        # end class lat

    # end class _Attributes

# end class Location

_Ancestor_Essence = MOM.Object

class Person (_Ancestor_Essence) :
    """Model a person of the Better Mouse Trap application."""

    PNS = BMT

    class _Attributes (_Ancestor_Essence._Attributes) :

        class last_name (A_String) :
            """Last name of person"""

            kind        = Attr.Primary
            ignore_case = True
            rank        = 1

        # end class last_name

        class first_name (A_String) :
            """First name of person"""

            kind        = Attr.Primary
            ignore_case = True
            rank        = 2
            ui_name     = "First name"

        # end class first_name

        class middle_name (A_String) :
            """Middle name of person"""

            kind        = Attr.Primary_Optional
            ignore_case = True
            max_length  = 5
            rank        = 1
            ui_name     = "Middle name"

        # end class middle_name

        class height (_A_Unit_, A_Int) :
            """Height of person"""

            kind               = Attr.Optional
            typ                = "height"
            _default_unit      = "m"
            _unit_dict         = dict \
                ( { "in"   : 25.4 }
                , cm       = 1.0e1
                , dm       = 1.0e2
                , ft       = 304.8
                , m        = 1.0e3
                , mm       = 1
                , yd       = 9144
                )

        # end class height

    # end class _Attributes

# end class Person

_Ancestor_Essence = Named_Object

class Rodent (_Ancestor_Essence) :
    """Model a rodent of the Better Mouse Trap application."""

    PNS    = BMT

    default_child = "BMT.Rat"

    is_partial    = True
    is_relevant   = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        class color (A_String) :
            """Color of the rodent"""

            kind     = Attr.Optional

        # end class color

        class weight (A_Float) :
            """Weight of the rodent"""

            kind     = Attr.Necessary
            check    = ("value > 0", )

        # end class weight

    # end class _Attributes

# end class Rodent

_Ancestor_Essence = Rodent

class Mouse (_Ancestor_Essence) :
    """Model a mouse of the Better Mouse Trap application."""

# end class Mouse

_Ancestor_Essence = Rodent

class Rat (_Ancestor_Essence) :
    """Model a rat of the Better Mouse Trap application."""

# end class Rat

_Ancestor_Essence = Mouse

class Beaver (_Ancestor_Essence) :
    """Model a beaver of the Better Mouse Trap application."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        class region (A_String) :
            """In which are lives the beaver"""

            kind     = Attr.Optional

        # end class region

    # end class _Attributes

# end class Beaver

_Ancestor_Essence = Beaver

class Otter (_Ancestor_Essence) :

    class _Attributes (_Ancestor_Essence._Attributes) :

        class river (A_String) :

            kind       = Attr.Optional
            max_length = 20

        # end class river

    # end class _Attributes

# end class Otter

_Ancestor_Essence = Named_Object

class Trap (_Ancestor_Essence) :
    """Model a trap of the Better Mouse Trap application."""

    PNS = BMT

    class _Attributes (_Ancestor_Essence._Attributes) :

        class max_weight (A_Float) :
            """Maximum weight of rodent the trap can hold"""

            kind     = Attr.Optional
            check    = ("value > 0", )
            ui_name  = "Maximum weight"

        # end class max_weight

        class serial_no (A_Int) :
            """Serial number of the trap"""

            kind     = Attr.Primary
            ui_name  = "Serial number"

        # end class serial_no

        class reaction_time_range (A_Int_Interval_C) :
            """Specified time-range in ms for the trap to close."""

            kind     = Attr.Optional

        # end class reaction_time_range

        class up_ex (A_Float) :
            """Example for an attribute that depends on other
               attributes and is automatically changed whenever one of
               those changes.
            """

            kind               = Attr.Cached
            auto_up_depends    = ("max_weight", "serial_no")

            def computed (self, obj) :
                if obj.max_weight :
                    return obj.max_weight * obj.serial_no
            # end def computed

        # end class up_ex

        class up_ex_q (A_Float) :
            """Example for a query attribute that is recomputed
               whenever one of the attributes it depends on changes.
            """

            kind                   = Attr.Query
            query                  = Q.max_weight * Q.serial_no
            query_preconditions    = (Q.max_weight, Q.serial_no)

        # end class up_ex_q

    # end class _Attributes

# end class Trap

_Ancestor_Essence = Trap

class Supertrap (_Ancestor_Essence) :
    """An enormously improved Trap."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class weights (A_Float_Interval) :
            """Range of weights this trap can safely hold"""

            kind               = Attr.Necessary

        # end class weights

    # end class _Attributes

# end class Supertrap

_Ancestor_Essence = MOM.Link1

class Rodent_is_sick (_Ancestor_Essence) :
    """Model the sickness of a rodent."""

    PNS = BMT

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :
            """Rodent that is sick"""

            role_type          = Rodent
            link_ref_attr_name = "sickness"
            link_ref_suffix    = None

        # end class left

        class sick_leave (A_Date_Interval) :
            """Duration of sick leave"""

            kind               = Attr.Primary

        # end class sick_leave

        class fever (A_Float) :
            """Highest temperature during the sickness"""

            kind               = Attr.Optional

        # end class fever
    # end class _Attributes

# end class Rodent_is_sick

_Ancestor_Essence = MOM.Link1

class Expected_Traptime (_Ancestor_Essence) :
    """Model the expected time until rodent is trapped."""

    PNS = BMT

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :
            """Rodent to which this expectation applies"""

            role_type          = Rodent
            link_ref_attr_name = "traptime"
            link_ref_suffix    = None

        # end class left

        class expected_traptime (A_Date_Time_Delta) :
            """Expected time until trapped"""

            kind               = Attr.Primary

        # end class expected_traptime

    # end class _Attributes

# end class Expected_Traptime

_Ancestor_Essence = MOM.Link2

class Rodent_in_Trap (_Ancestor_Essence) :
    """Model a rodent caught in a trap."""

    PNS = BMT

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :
            """Rodent caught in Trap."""

            role_type     = Rodent
            max_links     = 1
            auto_rev_ref  = "catch"

        # end class left

        class right (_Ancestor.right) :
            """Trap that caught a rodent."""

            role_type     = Trap
            max_links     = 1
            auto_rev_ref  = "catcher"

        # end class right

    # end class _Attributes

    class _Predicates (_Ancestor_Essence._Predicates) :

        class valid_weight (Pred.Condition) :
            """Weight of `rodent` must not exceed `max_weight` of `trap`."""

            kind          = Pred.System
            assertion     = "rodent.weight <= trap.max_weight"
            attributes    = ("rodent.weight", "trap.max_weight")

        # end class valid_weight

    # end class _Predicates


# end class Rodent_in_Trap

_Ancestor_Essence = MOM.Link2

class Person_owns_Trap (_Ancestor_Essence) :

    PNS = BMT

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :
            """Person owning the Trap."""

            role_name          = "owner"
            role_type          = Person
            auto_rev_ref       = True
            link_ref_attr_name = "owns_trap"

        # end class left

        class right (_Ancestor.right) :
            """Trap owned by person."""

            role_type          = Trap
            max_links          = 1
            auto_rev_ref       = True

        # end class right

        class price (A_Float) :
            kind               = Attr.Optional
            default            = 42.0
        # end class price

    # end class _Attributes

# end class Person_owns_Trap

_Ancestor_Essence = MOM.Link2

class Person_sets_Trap (_Ancestor_Essence) :

    PNS = BMT

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :
            """Person setting a trap."""

            role_name          = "setter"
            role_type          = Person
            auto_rev_ref       = True
            rev_ref_singular   = True
            link_ref_attr_name = "sets_trap"

        # end class left

        class right (_Ancestor.right) :

            role_type          = Trap
            max_links          = 1

        # end class right

        class location (A_Id_Entity) :
            """Location where a trap is set."""

            kind               = Attr.Primary
            P_Type             = Location

        # end class location

    # end class _Attributes

# end class Person_sets_Trap

def show (e) :
    if isinstance (e, (list, TFL._Q_Result_)) :
        print ("[%s]" % (", ".join (str (x) for x in e), ))
    else :
        print (e)
# end def show

### All classes defining `__getslice__` have been changed to be
### compatible to Python 3.x by changing `__getitem__` to deal with
### slices
###
### Unfortunately, in Python 2.x `__getslice__` is still necessary and
### code like::
###
###     self.kill_callback [:]
###
### triggers the warning::
###
### DeprecationWarning: in 3.x, __getslice__ has been removed; use __getitem__
###
import warnings
warnings.filterwarnings \
    ( "ignore", "in 3.x, __getslice__ has been removed; use __getitem__")
if 0 :
    warnings.filterwarnings \
        ( "error",  "comparing unequal types not supported in 3.x")

### Because the example classes are all defined here and not in their
### own package namespace, we'll fake it
BMT._Export ("*", "Version")

NL = chr (10)

### «text»

dt_form = \
"""
How to define and use essential object models
==============================================

Using `MOM`, an essential object model is specified by deriving
classes from :class:`MOM.Object<_MOM.Object.Object>` or from one of
the arity-specific descendants of :class:`MOM.Link<_MOM.Link.Link>`.

Each essential class must be defined inside a
:class:`TFL.Package_Namespace<_TFL.Package_Namespace.Package_Namespace>`
and the class definition must contain an explicit or inherited
reference :attr:`PNS<_MOM.Entity.PNS>` to that package
namespace.

Normally, each essential class is defined in a module of its own. In
some cases, a single module might define more than one essential
class.

The module `_MOM.import_MOM` provides all classes necessary to define
essential object or link types and is meant to be imported like::

    >>> from _MOM.import_MOM import *

An essential class as defined by its module isn't usable before an
app-type is created.

    >>> BMT.Person
    <class 'BMT.Person' [Spec Essence]>
    >>> BMT.Rodent
    <class 'BMT.Rodent' [Spec Essence]>
    >>> BMT.Beaver
    <class 'BMT.Beaver' [Spec Essence]>
    >>> BMT.Person_owns_Trap
    <class 'BMT.Person_owns_Trap' [Spec Essence]>
    >>> BMT.Person.last_name
    Traceback (most recent call last):
        ...
    AttributeError: type object 'Person' has no attribute 'last_name'


Application type
----------------

Before an essential object model can be used, the
:class:`application type<_MOM.App_Type.App_Type>` and at least one
:class:`derived application type<_MOM.App_Type._App_Type_D_>` must be
defined:

    >>> %(import_EMS)s as EMS
    >>> %(import_DBW)s as DBW
    >>> try :
    ...   apt = MOM.App_Type ("BMT", BMT).Derived (EMS, DBW)
    ... except Exception as exc :
    ...   import traceback; traceback.print_exc ()
    ...   import os; os.abort ()

Creating a derived app-type replaces the specification of the
essential classes with bare essential classes:

    >>> BMT.Person
    <class 'BMT.Person' [Bare Essence]>
    >>> BMT.Rodent
    <class 'BMT.Rodent' [Bare Essence]>
    >>> BMT.Beaver
    <class 'BMT.Beaver' [Bare Essence]>
    >>> BMT.Person_owns_Trap
    <class 'BMT.Person_owns_Trap' [Bare Essence]>

and derives an app-type specific entity-type for each of the essential
classes:

    >>> ET_Entity    = apt.entity_type ("MOM.Entity")
    >>> ET_Id_Entity = apt.entity_type ("MOM.Id_Entity")
    >>> ET_Named_Obj = apt.entity_type ("MOM.Named_Object")
    >>> ET_Person    = apt.entity_type ("BMT.Person")
    >>> ET_Mouse     = apt ["BMT.Mouse"]
    >>> ET_Rat       = apt ["BMT.Rat"]
    >>> ET_Rodent    = apt ["BMT.Rodent"]
    >>> ET_Trap      = apt ["BMT.Trap"]
    >>> ET_Supertrap = apt ["BMT.Supertrap"]

    >>> issubclass (ET_Mouse, BMT.Rodent)
    True
    >>> issubclass (ET_Mouse, BMT.Mouse)
    True
    >>> issubclass (ET_Rodent, BMT.Mouse)
    False

    >>> issubclass (ET_Mouse, BMT.Mouse.E_Spec)
    True

For each `entity_type` with a unique :attr:`epk_sig`, the meta
machinery automatically creates methods `epkified_ckd` and
`epkified_raw` matching the `epk_sig`. These auto-generated methods
are used by `__init__` to ensure that the required parameters are
passed for the :ref:`essential primary keys<essential-primary-keys>`.

    >>> for et in apt._T_Extension :
    ...   if et.epk_sig and "epkified_ckd" in et.__dict__ :
    ...     print ("***", et.type_name, "***", et.epk_sig)
    ...     print (et.epkified_ckd.source_code.rstrip ())
    ...     print (et.epkified_raw.source_code.rstrip ())
    ...
    *** MOM.Link *** ('left',)
    def epkified_ckd (cls, left, ** kw) :
        return (left,), kw
    def epkified_raw (cls, left, ** kw) :
        return (left,), kw
    *** MOM.Link1 *** ('left',)
    def epkified_ckd (cls, left, ** kw) :
        return (left,), kw
    def epkified_raw (cls, left, ** kw) :
        return (left,), kw
    *** MOM._Link_n_ *** ('left', 'right')
    def epkified_ckd (cls, left, right, ** kw) :
        return (left, right), kw
    def epkified_raw (cls, left, right, ** kw) :
        return (left, right), kw
    *** MOM.Link2 *** ('left', 'right')
    def epkified_ckd (cls, left, right, ** kw) :
        return (left, right), kw
    def epkified_raw (cls, left, right, ** kw) :
        return (left, right), kw
    *** MOM.Link3 *** ('left', 'middle', 'right')
    def epkified_ckd (cls, left, middle, right, ** kw) :
        return (left, middle, right), kw
    def epkified_raw (cls, left, middle, right, ** kw) :
        return (left, middle, right), kw
    *** MOM.Named_Object *** ('name',)
    def epkified_ckd (cls, name, ** kw) :
        return (name,), kw
    def epkified_raw (cls, name, ** kw) :
        return (name,), kw
    *** BMT.Location *** ('lon', 'lat')
    def epkified_ckd (cls, lon, lat, ** kw) :
        return (lon, lat), kw
    def epkified_raw (cls, lon, lat, ** kw) :
        return (lon, lat), kw
    *** BMT.Person *** ('last_name', 'first_name', 'middle_name')
    def epkified_ckd (cls, last_name, first_name, middle_name = '', ** kw) :
        return (last_name, first_name, middle_name), kw
    def epkified_raw (cls, last_name, first_name, middle_name = '', ** kw) :
        return (last_name, first_name, middle_name), kw
    *** BMT.Rodent *** ('name',)
    def epkified_ckd (cls, name, ** kw) :
        return (name,), kw
    def epkified_raw (cls, name, ** kw) :
        return (name,), kw
    *** BMT.Mouse *** ('name',)
    def epkified_ckd (cls, name, ** kw) :
        return (name,), kw
    def epkified_raw (cls, name, ** kw) :
        return (name,), kw
    *** BMT.Rat *** ('name',)
    def epkified_ckd (cls, name, ** kw) :
        return (name,), kw
    def epkified_raw (cls, name, ** kw) :
        return (name,), kw
    *** BMT.Beaver *** ('name',)
    def epkified_ckd (cls, name, ** kw) :
        return (name,), kw
    def epkified_raw (cls, name, ** kw) :
        return (name,), kw
    *** BMT.Otter *** ('name',)
    def epkified_ckd (cls, name, ** kw) :
        return (name,), kw
    def epkified_raw (cls, name, ** kw) :
        return (name,), kw
    *** BMT.Trap *** ('name', 'serial_no')
    def epkified_ckd (cls, name, serial_no, ** kw) :
        return (name, serial_no), kw
    def epkified_raw (cls, name, serial_no, ** kw) :
        return (name, serial_no), kw
    *** BMT.Supertrap *** ('name', 'serial_no')
    def epkified_ckd (cls, name, serial_no, ** kw) :
        return (name, serial_no), kw
    def epkified_raw (cls, name, serial_no, ** kw) :
        return (name, serial_no), kw
    *** BMT.Rodent_is_sick *** ('left', 'sick_leave')
    def epkified_ckd (cls, left, sick_leave, ** kw) :
        return (left, sick_leave), kw
    def epkified_raw (cls, left, sick_leave, ** kw) :
        return (left, sick_leave), kw
    *** BMT.Expected_Traptime *** ('left', 'expected_traptime')
    def epkified_ckd (cls, left, expected_traptime, ** kw) :
        return (left, expected_traptime), kw
    def epkified_raw (cls, left, expected_traptime, ** kw) :
        return (left, expected_traptime), kw
    *** BMT.Rodent_in_Trap *** ('left', 'right')
    def epkified_ckd (cls, left, right, ** kw) :
        return (left, right), kw
    def epkified_raw (cls, left, right, ** kw) :
        return (left, right), kw
    *** BMT.Person_owns_Trap *** ('left', 'right')
    def epkified_ckd (cls, left, right, ** kw) :
        return (left, right), kw
    def epkified_raw (cls, left, right, ** kw) :
        return (left, right), kw
    *** BMT.Person_sets_Trap *** ('left', 'right', 'location')
    def epkified_ckd (cls, left, right, location, ** kw) :
        return (left, right, location), kw
    def epkified_raw (cls, left, right, location, ** kw) :
        return (left, right, location), kw

    >>> for et in apt._T_Extension :
    ...   if et.args_as_kw :
    ...     print ("***", et.type_name, "***", getattr (et, "usr_sig", "") or getattr (et, "epk_sig", ""))
    ...     print (et.args_as_kw and et.args_as_kw.source_code.rstrip ())
    *** MOM.Link *** ('left',)
    def args_as_kw (cls, left = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("left", left)] if v is not undefined)
        return kw
    *** MOM.Link1 *** ('left',)
    def args_as_kw (cls, left = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("left", left)] if v is not undefined)
        return kw
    *** MOM._Link_n_ *** ('left', 'right')
    def args_as_kw (cls, left = undefined, right = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("left", left), ("right", right)] if v is not undefined)
        return kw
    *** MOM.Link2 *** ('left', 'right')
    def args_as_kw (cls, left = undefined, right = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("left", left), ("right", right)] if v is not undefined)
        return kw
    *** MOM.Link3 *** ('left', 'middle', 'right')
    def args_as_kw (cls, left = undefined, middle = undefined, right = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("left", left), ("middle", middle), ("right", right)] if v is not undefined)
        return kw
    *** MOM.Date_Interval *** ('start', 'finish')
    def args_as_kw (cls, start = undefined, finish = undefined) :
        kw = dict ((k, v) for k, v in [("start", start), ("finish", finish)] if v is not undefined)
        return kw
    *** MOM.Date_Interval_C *** ('start', 'finish')
    def args_as_kw (cls, start = undefined, finish = undefined) :
        kw = dict ((k, v) for k, v in [("start", start), ("finish", finish)] if v is not undefined)
        return kw
    *** MOM.Date_Interval_N *** ('start', 'finish')
    def args_as_kw (cls, start = undefined, finish = undefined) :
        kw = dict ((k, v) for k, v in [("start", start), ("finish", finish)] if v is not undefined)
        return kw
    *** MOM.Float_Interval *** ('lower', 'upper')
    def args_as_kw (cls, lower = undefined, upper = undefined) :
        kw = dict ((k, v) for k, v in [("lower", lower), ("upper", upper)] if v is not undefined)
        return kw
    *** MOM.Frequency_Interval *** ('lower', 'upper')
    def args_as_kw (cls, lower = undefined, upper = undefined) :
        kw = dict ((k, v) for k, v in [("lower", lower), ("upper", upper)] if v is not undefined)
        return kw
    *** MOM.Int_Interval *** ('lower', 'upper')
    def args_as_kw (cls, lower = undefined, upper = undefined) :
        kw = dict ((k, v) for k, v in [("lower", lower), ("upper", upper)] if v is not undefined)
        return kw
    *** MOM.Int_Interval_C *** ('lower', 'upper')
    def args_as_kw (cls, lower = undefined, upper = undefined) :
        kw = dict ((k, v) for k, v in [("lower", lower), ("upper", upper)] if v is not undefined)
        return kw
    *** MOM.Position *** ('lat', 'lon', 'height')
    def args_as_kw (cls, lat = undefined, lon = undefined, height = undefined) :
        kw = dict ((k, v) for k, v in [("lat", lat), ("lon", lon), ("height", height)] if v is not undefined)
        return kw
    *** MOM.Named_Object *** ('name',)
    def args_as_kw (cls, name = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("name", name)] if v is not undefined)
        return kw
    *** BMT.Location *** ('lon', 'lat')
    def args_as_kw (cls, lon = undefined, lat = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("lon", lon), ("lat", lat)] if v is not undefined)
        return kw
    *** BMT.Person *** ('last_name', 'first_name', 'middle_name')
    def args_as_kw (cls, last_name = undefined, first_name = undefined, middle_name = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("last_name", last_name), ("first_name", first_name), ("middle_name", middle_name)] if v is not undefined)
        return kw
    *** BMT.Rodent *** ('name',)
    def args_as_kw (cls, name = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("name", name)] if v is not undefined)
        return kw
    *** BMT.Mouse *** ('name',)
    def args_as_kw (cls, name = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("name", name)] if v is not undefined)
        return kw
    *** BMT.Rat *** ('name',)
    def args_as_kw (cls, name = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("name", name)] if v is not undefined)
        return kw
    *** BMT.Beaver *** ('name',)
    def args_as_kw (cls, name = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("name", name)] if v is not undefined)
        return kw
    *** BMT.Otter *** ('name',)
    def args_as_kw (cls, name = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("name", name)] if v is not undefined)
        return kw
    *** BMT.Trap *** ('name', 'serial_no')
    def args_as_kw (cls, name = undefined, serial_no = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("name", name), ("serial_no", serial_no)] if v is not undefined)
        return kw
    *** BMT.Supertrap *** ('name', 'serial_no')
    def args_as_kw (cls, name = undefined, serial_no = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("name", name), ("serial_no", serial_no)] if v is not undefined)
        return kw
    *** BMT.Rodent_is_sick *** ('left', 'sick_leave')
    def args_as_kw (cls, left = undefined, sick_leave = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("left", left), ("sick_leave", sick_leave)] if v is not undefined)
        return kw
    *** BMT.Expected_Traptime *** ('left', 'expected_traptime')
    def args_as_kw (cls, left = undefined, expected_traptime = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("left", left), ("expected_traptime", expected_traptime)] if v is not undefined)
        return kw
    *** BMT.Rodent_in_Trap *** ('left', 'right')
    def args_as_kw (cls, left = undefined, right = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("left", left), ("right", right)] if v is not undefined)
        return kw
    *** BMT.Person_owns_Trap *** ('left', 'right')
    def args_as_kw (cls, left = undefined, right = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("left", left), ("right", right)] if v is not undefined)
        return kw
    *** BMT.Person_sets_Trap *** ('left', 'right', 'location')
    def args_as_kw (cls, left = undefined, right = undefined, location = undefined, ** kw) :
        kw = dict (kw)
        kw.update ((k, v) for k, v in [("left", left), ("right", right), ("location", location)] if v is not undefined)
        return kw

Each entity_type knows about its children:

    >>> for et in apt._T_Extension :
    ...   if et.children :
    ...     print (et.type_name)
    ...     print ("   ", sorted (et.children))
    MOM.Entity
        ['MOM.An_Entity', 'MOM.Id_Entity', 'MOM.MD_Entity']
    MOM.An_Entity
        ['MOM.Date_Interval', 'MOM.Position', 'MOM._Interval_']
    MOM.Id_Entity
        ['MOM.Link', 'MOM.Object']
    MOM.MD_Entity
        ['MOM.MD_Change']
    MOM.Link
        ['MOM.Link1', 'MOM._Link_n_']
    MOM.Link1
        ['BMT.Expected_Traptime', 'BMT.Rodent_is_sick']
    MOM._Link_n_
        ['MOM.Link2', 'MOM.Link3']
    MOM.Link2
        ['BMT.Person_owns_Trap', 'BMT.Person_sets_Trap', 'BMT.Rodent_in_Trap']
    MOM.Object
        ['BMT.Location', 'BMT.Person', 'MOM.Named_Object']
    MOM.Date_Interval
        ['MOM.Date_Interval_C', 'MOM.Date_Interval_N']
    MOM._Interval_
        ['MOM.Float_Interval', 'MOM.Frequency_Interval', 'MOM.Int_Interval']
    MOM.Int_Interval
        ['MOM.Int_Interval_C']
    MOM.Named_Object
        ['BMT.Rodent', 'BMT.Trap']
    BMT.Rodent
        ['BMT.Mouse', 'BMT.Rat']
    BMT.Mouse
        ['BMT.Beaver']
    BMT.Beaver
        ['BMT.Otter']
    BMT.Trap
        ['BMT.Supertrap']

    >>> for et in apt._T_Extension :
    ...   if et.children and et.children != et.children_np :
    ...     print (et.type_name)
    ...     print ("   ", sorted (et.children))
    ...     print ("   ", sorted (et.children_np))
    MOM.Entity
        ['MOM.An_Entity', 'MOM.Id_Entity', 'MOM.MD_Entity']
        ['BMT.Expected_Traptime', 'BMT.Location', 'BMT.Mouse', 'BMT.Person', 'BMT.Person_owns_Trap', 'BMT.Person_sets_Trap', 'BMT.Rat', 'BMT.Rodent_in_Trap', 'BMT.Rodent_is_sick', 'BMT.Trap', 'MOM.Date_Interval', 'MOM.Float_Interval', 'MOM.Frequency_Interval', 'MOM.Int_Interval', 'MOM.MD_Change', 'MOM.Position']
    MOM.An_Entity
        ['MOM.Date_Interval', 'MOM.Position', 'MOM._Interval_']
        ['MOM.Date_Interval', 'MOM.Float_Interval', 'MOM.Frequency_Interval', 'MOM.Int_Interval', 'MOM.Position']
    MOM.Id_Entity
        ['MOM.Link', 'MOM.Object']
        ['BMT.Expected_Traptime', 'BMT.Location', 'BMT.Mouse', 'BMT.Person', 'BMT.Person_owns_Trap', 'BMT.Person_sets_Trap', 'BMT.Rat', 'BMT.Rodent_in_Trap', 'BMT.Rodent_is_sick', 'BMT.Trap']
    MOM.Link
        ['MOM.Link1', 'MOM._Link_n_']
        ['BMT.Expected_Traptime', 'BMT.Person_owns_Trap', 'BMT.Person_sets_Trap', 'BMT.Rodent_in_Trap', 'BMT.Rodent_is_sick']
    MOM._Link_n_
        ['MOM.Link2', 'MOM.Link3']
        ['BMT.Person_owns_Trap', 'BMT.Person_sets_Trap', 'BMT.Rodent_in_Trap']
    MOM.Object
        ['BMT.Location', 'BMT.Person', 'MOM.Named_Object']
        ['BMT.Location', 'BMT.Mouse', 'BMT.Person', 'BMT.Rat', 'BMT.Trap']
    MOM.Named_Object
        ['BMT.Rodent', 'BMT.Trap']
        ['BMT.Mouse', 'BMT.Rat', 'BMT.Trap']


The app-type specific entity-types are ready to be used by
:class:`scopes<_MOM.Scope.Scope>` and their
:mod:`etype managers<_MOM.E_Type_Manager>`:

    >>> ET_Person
    <class 'BMT.Person' [BMT__Hash__HPS]>
    >>> ET_Person.Essence
    <class 'BMT.Person' [Bare Essence]>
    >>> ET_Person.E_Spec
    <class 'BMT.Person' [Spec Essence]>
    >>> ET_Person.primary
    [String `last_name`, String `first_name`, String `middle_name`]
    >>> [attr.__class__.__name__ for attr in ET_Person.primary]
    ['Primary__Raw_Value', 'Primary__Raw_Value', 'Primary_Optional__Raw_Value']
    >>> ET_Person.necessary
    []
    >>> ET_Person.optional
    [height `height`]

    >>> ET_Mouse.primary
    [Name `name`]
    >>> ET_Mouse.necessary
    [Float `weight`]
    >>> ET_Mouse.optional
    [String `color`]
    >>> sorted (pyk.itervalues (ET_Mouse.attributes), key = TFL.Getter.name)
    [Blob `FO`, Role_Ref `catcher`, String `color`, Entity `created_by`, Rev_Ref `creation`, Date-Time `creation_date`, Boolean `electric`, Int `is_used`, Rev_Ref `last_change`, Date-Time `last_changed`, Entity `last_changed_by`, Int `last_cid`, Name `name`, Surrogate `pid`, Boolean `playback_p`, Link_Ref_List `sickness`, Link_Ref `trap_link`, Link_Ref_List `trap_links`, Link_Ref_List `traptime`, String `type_name`, String `ui_display`, String `ui_repr`, Float `weight`, Boolean `x_locked`]

    >>> last_name_prop = ET_Person.attr_prop ("last_name")
    >>> prepr ((last_name_prop.name, last_name_prop.ui_name))
    ('last_name', 'Last name')
    >>> sorted (ET_Person._Attributes._own_names)
    ['first_name', 'height', 'last_name', 'middle_name', 'owns_trap_links', 'sets_trap_links', 'traps']

    >>> color_prop = ET_Mouse.attr_prop ("color")
    >>> prepr ((color_prop.name, color_prop.ui_name))
    ('color', 'Color')

    >>> sorted (ET_Trap._Attributes._own_names)
    ['catch', 'max_weight', 'owner', 'owner_link', 'owner_links', 'reaction_time_range', 'rodent_link', 'rodent_links', 'serial_no', 'setter', 'setter_link', 'setter_links', 'up_ex', 'up_ex_q']
    >>> sorted (ET_Supertrap._Attributes._own_names)
    ['weights']
    >>> sorted (ET_Trap._Attributes._names)
    ['FO', 'catch', 'created_by', 'creation', 'creation_date', 'electric', 'is_used', 'last_change', 'last_changed', 'last_changed_by', 'last_cid', 'max_weight', 'name', 'owner', 'owner_link', 'owner_links', 'pid', 'playback_p', 'reaction_time_range', 'rodent_link', 'rodent_links', 'serial_no', 'setter', 'setter_link', 'setter_links', 'type_name', 'ui_display', 'ui_repr', 'up_ex', 'up_ex_q', 'x_locked']
    >>> sorted (ET_Supertrap._Attributes._names)
    ['FO', 'catch', 'created_by', 'creation', 'creation_date', 'electric', 'is_used', 'last_change', 'last_changed', 'last_changed_by', 'last_cid', 'max_weight', 'name', 'owner', 'owner_link', 'owner_links', 'pid', 'playback_p', 'reaction_time_range', 'rodent_link', 'rodent_links', 'serial_no', 'setter', 'setter_link', 'setter_links', 'type_name', 'ui_display', 'ui_repr', 'up_ex', 'up_ex_q', 'weights', 'x_locked']
    >>> sorted (pyk.itervalues (ET_Trap.attributes), key = TFL.Getter.name)
    [Blob `FO`, Role_Ref `catch`, Entity `created_by`, Rev_Ref `creation`, Date-Time `creation_date`, Boolean `electric`, Int `is_used`, Rev_Ref `last_change`, Date-Time `last_changed`, Entity `last_changed_by`, Int `last_cid`, Float `max_weight`, Name `name`, Role_Ref `owner`, Link_Ref `owner_link`, Link_Ref_List `owner_links`, Surrogate `pid`, Boolean `playback_p`, Int_Interval `reaction_time_range`, Link_Ref `rodent_link`, Link_Ref_List `rodent_links`, Int `serial_no`, Role_Ref `setter`, Link_Ref `setter_link`, Link_Ref_List `setter_links`, String `type_name`, String `ui_display`, String `ui_repr`, Float `up_ex`, Float `up_ex_q`, Boolean `x_locked`]
    >>> sorted (pyk.itervalues (ET_Supertrap.attributes), key = TFL.Getter.name)
    [Blob `FO`, Role_Ref `catch`, Entity `created_by`, Rev_Ref `creation`, Date-Time `creation_date`, Boolean `electric`, Int `is_used`, Rev_Ref `last_change`, Date-Time `last_changed`, Entity `last_changed_by`, Int `last_cid`, Float `max_weight`, Name `name`, Role_Ref `owner`, Link_Ref `owner_link`, Link_Ref_List `owner_links`, Surrogate `pid`, Boolean `playback_p`, Int_Interval `reaction_time_range`, Link_Ref `rodent_link`, Link_Ref_List `rodent_links`, Int `serial_no`, Role_Ref `setter`, Link_Ref `setter_link`, Link_Ref_List `setter_links`, String `type_name`, String `ui_display`, String `ui_repr`, Float `up_ex`, Float `up_ex_q`, Float_Interval `weights`, Boolean `x_locked`]

    >>> print (portable_repr (sorted (ET_Id_Entity.relevant_roots)))
    ['BMT.Expected_Traptime', 'BMT.Location', 'BMT.Person', 'BMT.Person_owns_Trap', 'BMT.Person_sets_Trap', 'BMT.Rodent', 'BMT.Rodent_in_Trap', 'BMT.Rodent_is_sick', 'BMT.Trap']
    >>> ET_Person.relevant_root
    <class 'BMT.Person' [BMT__Hash__HPS]>
    >>> ET_Rodent.relevant_root
    <class 'BMT.Rodent' [BMT__Hash__HPS]>
    >>> ET_Mouse.relevant_root
    <class 'BMT.Rodent' [BMT__Hash__HPS]>

    >>> sorted (ET_Person.children)
    []
    >>> print (portable_repr (sorted (ET_Rodent.children)))
    ['BMT.Mouse', 'BMT.Rat']
    >>> sorted (pyk.itervalues (ET_Rodent.children), key = TFL.Getter.type_name)
    [<class 'BMT.Mouse' [BMT__Hash__HPS]>, <class 'BMT.Rat' [BMT__Hash__HPS]>]
    >>> sorted (ET_Rat.children)
    []

    >>> print (portable_repr (sorted (apt.etypes)))
    ['BMT.Beaver', 'BMT.Expected_Traptime', 'BMT.Location', 'BMT.Mouse', 'BMT.Otter', 'BMT.Person', 'BMT.Person_owns_Trap', 'BMT.Person_sets_Trap', 'BMT.Rat', 'BMT.Rodent', 'BMT.Rodent_in_Trap', 'BMT.Rodent_is_sick', 'BMT.Supertrap', 'BMT.Trap', 'MOM.An_Entity', 'MOM.Date_Interval', 'MOM.Date_Interval_C', 'MOM.Date_Interval_N', 'MOM.Entity', 'MOM.Float_Interval', 'MOM.Frequency_Interval', 'MOM.Id_Entity', 'MOM.Int_Interval', 'MOM.Int_Interval_C', 'MOM.Link', 'MOM.Link1', 'MOM.Link2', 'MOM.Link3', 'MOM.MD_Change', 'MOM.MD_Entity', 'MOM.Named_Object', 'MOM.Object', 'MOM.Position', 'MOM._Interval_', 'MOM._Link_n_']
    >>> print (portable_repr ([t.type_name for t in apt._T_Extension]))
    ['MOM.Entity', 'MOM.An_Entity', 'MOM.Id_Entity', 'MOM.MD_Entity', 'MOM.MD_Change', 'MOM.Link', 'MOM.Link1', 'MOM._Link_n_', 'MOM.Link2', 'MOM.Link3', 'MOM.Object', 'MOM.Date_Interval', 'MOM.Date_Interval_C', 'MOM.Date_Interval_N', 'MOM._Interval_', 'MOM.Float_Interval', 'MOM.Frequency_Interval', 'MOM.Int_Interval', 'MOM.Int_Interval_C', 'MOM.Position', 'MOM.Named_Object', 'BMT.Location', 'BMT.Person', 'BMT.Rodent', 'BMT.Mouse', 'BMT.Rat', 'BMT.Beaver', 'BMT.Otter', 'BMT.Trap', 'BMT.Supertrap', 'BMT.Rodent_is_sick', 'BMT.Expected_Traptime', 'BMT.Rodent_in_Trap', 'BMT.Person_owns_Trap', 'BMT.Person_sets_Trap']
    >>> for t in apt._T_Extension [2:] :
    ...     print ("%%-35s %%s" %% (t.type_name, t.epk_sig))
    MOM.Id_Entity                       ()
    MOM.MD_Entity                       ()
    MOM.MD_Change                       ()
    MOM.Link                            ('left',)
    MOM.Link1                           ('left',)
    MOM._Link_n_                        ('left', 'right')
    MOM.Link2                           ('left', 'right')
    MOM.Link3                           ('left', 'middle', 'right')
    MOM.Object                          ()
    MOM.Date_Interval                   ()
    MOM.Date_Interval_C                 ()
    MOM.Date_Interval_N                 ()
    MOM._Interval_                      ()
    MOM.Float_Interval                  ()
    MOM.Frequency_Interval              ()
    MOM.Int_Interval                    ()
    MOM.Int_Interval_C                  ()
    MOM.Position                        ()
    MOM.Named_Object                    ('name',)
    BMT.Location                        ('lon', 'lat')
    BMT.Person                          ('last_name', 'first_name', 'middle_name')
    BMT.Rodent                          ('name',)
    BMT.Mouse                           ('name',)
    BMT.Rat                             ('name',)
    BMT.Beaver                          ('name',)
    BMT.Otter                           ('name',)
    BMT.Trap                            ('name', 'serial_no')
    BMT.Supertrap                       ('name', 'serial_no')
    BMT.Rodent_is_sick                  ('left', 'sick_leave')
    BMT.Expected_Traptime               ('left', 'expected_traptime')
    BMT.Rodent_in_Trap                  ('left', 'right')
    BMT.Person_owns_Trap                ('left', 'right')
    BMT.Person_sets_Trap                ('left', 'right', 'location')

    >>> for t in apt._T_Extension [2:] :
    ...     print ("%%s%%s    %%s" %% (t.type_name, NL, portable_repr (t.sorted_by.criteria)))
    MOM.Id_Entity
        ('type_name', 'pid')
    MOM.MD_Entity
        ()
    MOM.MD_Change
        ('-cid',)
    MOM.Link
        ('left',)
    MOM.Link1
        ('left',)
    MOM._Link_n_
        ('left', 'right')
    MOM.Link2
        ('left', 'right')
    MOM.Link3
        ('left', 'middle', 'right')
    MOM.Object
        ('type_name', 'pid')
    MOM.Date_Interval
        ('start', 'finish')
    MOM.Date_Interval_C
        ('start', 'finish')
    MOM.Date_Interval_N
        ('start', 'finish')
    MOM._Interval_
        ('lower', 'upper')
    MOM.Float_Interval
        ('lower', 'upper')
    MOM.Frequency_Interval
        ('lower', 'upper')
    MOM.Int_Interval
        ('lower', 'upper')
    MOM.Int_Interval_C
        ('lower', 'upper')
    MOM.Position
        ('lat', 'lon', 'height')
    MOM.Named_Object
        ('name',)
    BMT.Location
        ('lon', 'lat')
    BMT.Person
        ('last_name', 'first_name', 'middle_name')
    BMT.Rodent
        ('name',)
    BMT.Mouse
        ('name',)
    BMT.Rat
        ('name',)
    BMT.Beaver
        ('name',)
    BMT.Otter
        ('name',)
    BMT.Trap
        ('name', 'serial_no')
    BMT.Supertrap
        ('name', 'serial_no')
    BMT.Rodent_is_sick
        ('left.name', 'sick_leave.start', 'sick_leave.finish')
    BMT.Expected_Traptime
        ('left.name', 'expected_traptime')
    BMT.Rodent_in_Trap
        ('left.name', 'right.name', 'right.serial_no')
    BMT.Person_owns_Trap
        ('left.last_name', 'left.first_name', 'left.middle_name', 'right.name', 'right.serial_no')
    BMT.Person_sets_Trap
        ('left.last_name', 'left.first_name', 'left.middle_name', 'right.name', 'right.serial_no', 'location.lon', 'location.lat')

    >>> show_ref_map (ET_Person, "Ref_Req_Map")
    BMT.Person
        ('BMT.Person_owns_Trap', ['left'])
        ('BMT.Person_sets_Trap', ['left'])
    >>> show_ref_map (ET_Trap,   "Ref_Req_Map")
    BMT.Trap
        ('BMT.Person_owns_Trap', ['right'])
        ('BMT.Person_sets_Trap', ['right'])
        ('BMT.Rodent_in_Trap', ['right'])

    >>> show_ref_map (ET_Person, "Ref_Opt_Map")
    >>> show_ref_map (ET_Trap,   "Ref_Opt_Map")

    >>> show_children (ET_Entity)
    MOM.Entity
      MOM.An_Entity
        MOM.Date_Interval
          MOM.Date_Interval_C
          MOM.Date_Interval_N
        MOM._Interval_
          MOM.Float_Interval
          MOM.Frequency_Interval
          MOM.Int_Interval
            MOM.Int_Interval_C
        MOM.Position
      MOM.Id_Entity
        MOM.Link
          MOM.Link1
            BMT.Rodent_is_sick
            BMT.Expected_Traptime
          MOM._Link_n_
            MOM.Link2
              BMT.Rodent_in_Trap
              BMT.Person_owns_Trap
              BMT.Person_sets_Trap
            MOM.Link3
        MOM.Object
          MOM.Named_Object
            BMT.Rodent
              BMT.Mouse
                BMT.Beaver
                  BMT.Otter
              BMT.Rat
            BMT.Trap
              BMT.Supertrap
          BMT.Location
          BMT.Person
      MOM.MD_Entity
        MOM.MD_Change

Scope
-----

A :class:`scope<_MOM.Scope.Scope>` manages the instances of essential
object and link types.

Specifying `None` as `db_url` will create an in memory database::

    >>> scope = MOM.Scope.new (apt, %(db_scheme)s)

For each :attr:`~_MOM.Entity.PNS` defining essential
classes, the `scope` provides an object holding
:class:`object managers<_MOM.E_Type_Manager.Object>` and
:class:`link managers<_MOM.E_Type_Manager.Link>`
that support instance creation and queries:

    .. ### DBW-specific start

    >>> scope.MOM.Id_Entity
    <E_Type_Manager for MOM.Id_Entity of scope BMT__Hash__HPS>
    >>> scope.BMT.Person
    <E_Type_Manager for BMT.Person of scope BMT__Hash__HPS>
    >>> scope.BMT.Person_owns_Trap
    <E_Type_Manager for BMT.Person_owns_Trap of scope BMT__Hash__HPS>

    .. ### DBW-specific finish

.. _`essential-primary-keys`:

Identity
--------

Essential objects and links have identity, i.e., each object or link
can be uniquely identified. This identity is specified by a set of (so
called `primary`) attributes that together define the
`essential primary key`, short `epk`, for the entity in question. If
there is more than one primary attribute, the sequence of the
attributes is defined by their :attr:`rank` and :attr:`name`.

Essential objects identified by a simple, unstructured `name` are
defined by classes derived from
:class:`MOM.Named_Object<_MOM.Object.Named_Object>`. All other
essential objects are defined by classes derived from
:class:`MOM.Object<_MOM.Object.Object>` that specify one or more
essential attributes of kind :class:`~_MOM._Attr.Kind.Primary`.

Essential links are identified by the associated objects (the link's
roles) and any other, if any, primary attributes defined for the link
in question:

- Unary links are derived from :class:`MOM.Link1<_MOM.Link.Link1>`
  and identified by the link role :attr:`left<_MOM.Link.Link1.left>`
  plus any other primary attributes.

- Binary links are derived from :class:`MOM.Link2<_MOM.Link.Link2>`
  and identified by the link roles :attr:`left<_MOM.Link.Link2.left>`
  and :attr:`right<_MOM.Link.Link2.right>` plus any other primary
  attributes.

- Ternary links are derived from :class:`MOM.Link3<_MOM.Link.Link3>`
  and identified by the link roles :attr:`left<_MOM.Link.Link3.left>`,
  :attr:`middle<_MOM.Link.Link3.middle>`,
  and :attr:`right<_MOM.Link.Link3.right>` plus any other primary
  attributes.

Object and link creation
-------------------------

One creates objects or links by calling the etype manager of the
appropriate class:

    >>> with expect_except (MOM.Error.Partial_Type) :
    ...     scope.MOM.Named_Object ("foo")
    Partial_Type: Named_Object

    >>> p     = scope.BMT.Person     ("luke", "lucky")
    >>> p
    BMT.Person ('luke', 'lucky', '')
    >>> q     = scope.BMT.Person     ("dog",  "snoopy")
    >>> l1    = scope.BMT.Location   (-16.268799, 48.189956)
    >>> l2    = scope.BMT.Location   (-16.740770, 48.463313)
    >>> m     = scope.BMT.Mouse      ("mighty_mouse")
    >>> b     = scope.BMT.Beaver     ("toothy_beaver")
    >>> r     = scope.BMT.Rat        ("rutty_rat")
    >>> axel  = scope.BMT.Rat        ("axel")
    >>> t1    = scope.BMT.Trap       ("x", 1)
    >>> t2    = scope.BMT.Trap       ("x", 2)
    >>> t3    = scope.BMT.Trap       ("y", 1)
    >>> t4    = scope.BMT.Trap       ("y", 2)
    >>> t5    = scope.BMT.Trap       ("z", 3)

    >>> Ris   = scope.BMT.Rodent_is_sick
    >>> RiT   = scope.BMT.Rodent_in_Trap
    >>> PoT   = scope.BMT.Person_owns_Trap
    >>> PTL   = scope.BMT.Person_sets_Trap
    >>> TT    = scope.BMT.Expected_Traptime

    >>> isinstance (p, scope.BMT.Person)
    True
    >>> issubclass (p.__class__, scope.BMT.Person)
    True
    >>> isinstance (p, scope.BMT.Rodent)
    False
    >>> issubclass (p.__class__, scope.BMT.Rodent)
    False

    >>> m == m, m != m, m == b, m != b, m == "", m != ""
    (True, False, False, True, False, True)

    >>> with expect_except (MOM.Error.Wrong_Type) :
    ...     RiT (p, t4)
    Wrong_Type: Person 'luke, lucky' not eligible for attribute left,
        must be instance of Rodent

    >>> rit1 = RiT (m, t1)
    >>> rit1
    BMT.Rodent_in_Trap (('mighty_mouse', ), ('x', 1))
    >>> with expect_except (MOM.Error.Multiplicity) :
    ...     RiT (m, t2)
    Multiplicity: The new definition of Rodent in Trap (BMT.Mouse ('mighty_mouse'), BMT.Trap ('x', 2)) would exceed the maximum number [1] of links allowed for BMT.Mouse ('mighty_mouse',).
      Already existing:
        BMT.Rodent_in_Trap (('mighty_mouse', 'BMT.Mouse'), ('x', '1', 'BMT.Trap'))
    >>> rit3 = RiT (r, t3)
    >>> rit3
    BMT.Rodent_in_Trap (('rutty_rat', ), ('y', 1))
    >>> RiT (axel, t2)
    BMT.Rodent_in_Trap (('axel', ), ('x', 2))

    >>> tt1 = TT (r, "1w 2d 2:2:17.5", raw = True)
    >>> tt1.expected_traptime
    datetime.timedelta(9, 7337, 500000)

    >>> PoT (p, t1)
    BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 1))
    >>> PoT (p, t2)
    BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 2))
    >>> PoT (q, t3)
    BMT.Person_owns_Trap (('dog', 'snoopy', ''), ('y', 1))
    >>> PoT (("tin", "tin"), t4)
    BMT.Person_owns_Trap (('tin', 'tin', ''), ('y', 2))

Creating a link will automatically change `auto_rev_ref` attributes of the
objects participating of the link, like `Trap.setter`::

    >>> t1.attr_prop ("setter")
    Role_Ref `setter`
    >>> t1.attr_prop ("setter_links")
    Link_Ref_List `setter_links`

    >>> print (t1.setter) ### before creation of Person_sets_Trap for t1
    None
    >>> PTL (p, t1, l1)
    BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956))

    >>> t1.setter ### after creation of Person_sets_Trap for t1
    BMT.Person ('luke', 'lucky', '')
    >>> t1.setter_links
    [BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956))]

    >>> print (t2.setter) ### before creation of Person_sets_Trap for t2
    None
    >>> PTL (p, t2, l2)
    BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313))
    >>> t2.setter ### after creation of Person_sets_Trap for t2
    BMT.Person ('luke', 'lucky', '')
    >>> t2.setter_links
    [BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313))]

    >>> print (t3.setter) ### before creation of Person_sets_Trap for t3
    None
    >>> PTL (p, t3, l2)
    BMT.Person_sets_Trap (('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313))
    >>> t3.setter ### after creation of Person_sets_Trap for t3
    BMT.Person ('luke', 'lucky', '')
    >>> t3.setter_links
    [BMT.Person_sets_Trap (('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313))]

Queries
-------

One queries the object model by calling query methods of the
appropriate etype manager. Strict queries return only instances
of the essential class in question,
but not instances of derived classes. Non-strict queries are
transitive, i.e., they return instances of the essential class in
question and all its descendants. For partial types, strict queries
return nothing. By default, queries are non-strict (transitive).
Passing `strict = True` to a query makes it strict.

The query :meth:`instance<_MOM.E_Type_Manager.E_Type_Manager.instance>` can
only be applied to `E_Type_Managers` for essential types that are, or
inherit from, a `relevant_root`:

    >>> scope.MOM.Object.instance ("mighty_mouse")
    Traceback (most recent call last):
      ...
    TypeError: Object needs the arguments (), got ('mighty_mouse',) instead
    >>> scope.MOM.Named_Object.instance ("mighty_mouse")
    BMT.Mouse ('mighty_mouse')

    >>> scope.BMT.Rodent.instance ("mighty_mouse")
    BMT.Mouse ('mighty_mouse')
    >>> print (scope.BMT.Rat.instance ("mighty_mouse"))
    None
    >>> print (scope.BMT.Rat.query (name = "mighty_mouse").all ())
    []

    >>> PoT.query_s ().all ()
    [BMT.Person_owns_Trap (('dog', 'snoopy', ''), ('y', 1)), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 1)), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 2)), BMT.Person_owns_Trap (('tin', 'tin', ''), ('y', 2))]
    >>> PoT.instance (('dog', 'snoopy'), ('y', 1))
    BMT.Person_owns_Trap (('dog', 'snoopy', ''), ('y', 1))
    >>> PoT.instance (('dog', 'snoopy', ''), ('x', 2))
    >>> print (PoT.instance (("Man", "tin"), t4))
    None

The query :meth:`exists<_MOM.E_Type_Manager.E_Type_Manager.exists>`
returns a list of all `E_Type_Managers` for which an object or link
with the specified `epk` exists:

    >>> scope.MOM.Named_Object.exists ("mighty_mouse")
    [<E_Type_Manager for BMT.Mouse of scope BMT__Hash__HPS>]
    >>> scope.BMT.Mouse.exists ("mighty_mouse")
    [<E_Type_Manager for BMT.Mouse of scope BMT__Hash__HPS>]
    >>> scope.BMT.Rat.exists ("mighty_mouse")
    []

    >>> PoT.exists (('dog', 'snoopy'), ('y', 1))
    [<E_Type_Manager for BMT.Person_owns_Trap of scope BMT__Hash__HPS>]
    >>> PoT.exists (("Man", "tin"), t4)
    []

The queries :attr:`~_MOM.E_Type_Manager.E_Type_Manager.count_strict`,
:attr:`~_MOM.E_Type_Manager.E_Type_Manager.count`,
:meth:`~_MOM.E_Type_Manager.E_Type_Manager.query`, and
:meth:`~_MOM.E_Type_Manager.E_Type_Manager.r_query` return the
number, or list, of instances of the specified
etype:

    >>> scope.BMT.Mouse.count_strict
    1
    >>> list (scope.BMT.Mouse.query_s (strict = True))
    [BMT.Mouse ('mighty_mouse')]
    >>> scope.BMT.Mouse.count
    2
    >>> list (scope.BMT.Mouse.query_s ())
    [BMT.Mouse ('mighty_mouse'), BMT.Beaver ('toothy_beaver')]

    >>> scope.BMT.Rat.count_strict
    2
    >>> list (scope.BMT.Rat.query_s (strict = True))
    [BMT.Rat ('axel'), BMT.Rat ('rutty_rat')]
    >>> scope.BMT.Rat.count
    2
    >>> list (scope.BMT.Rat.query_s ())
    [BMT.Rat ('axel'), BMT.Rat ('rutty_rat')]

    >>> scope.BMT.Rodent.count_strict
    0
    >>> list (scope.BMT.Rodent.query_s (strict = True))
    []
    >>> scope.BMT.Rodent.count
    4
    >>> list (scope.BMT.Rodent.query_s ())
    [BMT.Rat ('axel'), BMT.Mouse ('mighty_mouse'), BMT.Rat ('rutty_rat'), BMT.Beaver ('toothy_beaver')]

    >>> scope.MOM.Named_Object.count
    9
    >>> list (scope.MOM.Named_Object.query_s ())
    [BMT.Rat ('axel'), BMT.Mouse ('mighty_mouse'), BMT.Rat ('rutty_rat'), BMT.Beaver ('toothy_beaver'), BMT.Trap ('x', 1), BMT.Trap ('x', 2), BMT.Trap ('y', 1), BMT.Trap ('y', 2), BMT.Trap ('z', 3)]
    >>> scope.MOM.Object.count
    14
    >>> list (scope.MOM.Object.query_s ())
    [BMT.Location (-16.74077, 48.463313), BMT.Location (-16.268799, 48.189956), BMT.Rat ('axel'), BMT.Person ('dog', 'snoopy', ''), BMT.Person ('luke', 'lucky', ''), BMT.Mouse ('mighty_mouse'), BMT.Rat ('rutty_rat'), BMT.Person ('tin', 'tin', ''), BMT.Beaver ('toothy_beaver'), BMT.Trap ('x', 1), BMT.Trap ('x', 2), BMT.Trap ('y', 1), BMT.Trap ('y', 2), BMT.Trap ('z', 3)]

    >>> list (scope.MOM.Id_Entity.query_s ())
    [BMT.Location (-16.74077, 48.463313), BMT.Location (-16.268799, 48.189956), BMT.Rat ('axel'), BMT.Rodent_in_Trap (('axel', ), ('x', 2)), BMT.Person ('dog', 'snoopy', ''), BMT.Person_owns_Trap (('dog', 'snoopy', ''), ('y', 1)), BMT.Person ('luke', 'lucky', ''), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 1)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956)), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 2)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313)), BMT.Mouse ('mighty_mouse'), BMT.Rodent_in_Trap (('mighty_mouse', ), ('x', 1)), BMT.Rat ('rutty_rat'), BMT.Rodent_in_Trap (('rutty_rat', ), ('y', 1)), BMT.Expected_Traptime (('rutty_rat', ), 9 days, 2:02:17.500000), BMT.Person ('tin', 'tin', ''), BMT.Person_owns_Trap (('tin', 'tin', ''), ('y', 2)), BMT.Beaver ('toothy_beaver'), BMT.Trap ('x', 1), BMT.Trap ('x', 2), BMT.Trap ('y', 1), BMT.Trap ('y', 2), BMT.Trap ('z', 3)]
    >>> scope.MOM.Id_Entity.count
    25

    >>> scope.MOM.Link.count
    11
    >>> list (scope.MOM.Link.query_s ())
    [BMT.Rodent_in_Trap (('axel', ), ('x', 2)), BMT.Person_owns_Trap (('dog', 'snoopy', ''), ('y', 1)), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 1)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956)), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 2)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313)), BMT.Rodent_in_Trap (('mighty_mouse', ), ('x', 1)), BMT.Rodent_in_Trap (('rutty_rat', ), ('y', 1)), BMT.Expected_Traptime (('rutty_rat', ), 9 days, 2:02:17.500000), BMT.Person_owns_Trap (('tin', 'tin', ''), ('y', 2))]

    >>> scope.MOM.Link2.count
    10
    >>> list (scope.MOM.Link2.query_s ())
    [BMT.Rodent_in_Trap (('axel', ), ('x', 2)), BMT.Person_owns_Trap (('dog', 'snoopy', ''), ('y', 1)), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 1)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956)), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 2)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313)), BMT.Rodent_in_Trap (('mighty_mouse', ), ('x', 1)), BMT.Rodent_in_Trap (('rutty_rat', ), ('y', 1)), BMT.Person_owns_Trap (('tin', 'tin', ''), ('y', 2))]

    >>> sk_right_left = TFL.Sorted_By (RiT.right.sort_key, RiT.left.sort_key)
    >>> sk_right_left_pm = TFL.Sorted_By (RiT.right.sort_key_pm, RiT.left.sort_key_pm)
    >>> RiT.count
    3
    >>> show (RiT.query_s ())
    [(('axel', ), ('x', 2)), (('mighty_mouse', ), ('x', 1)), (('rutty_rat', ), ('y', 1))]
    >>> show (RiT.query_s (sort_key = sk_right_left))
    [(('mighty_mouse', ), ('x', 1)), (('axel', ), ('x', 2)), (('rutty_rat', ), ('y', 1))]

    >>> prepr (* sk_right_left (rit1)) #doctest: +NORMALIZE_WHITESPACE
    ('tuple', (('tuple', ('text-string', 'x')), ('tuple', ('number', 1)))) ('tuple', (('tuple', ('text-string', 'mighty_mouse')),))

    >>> prepr (* sk_right_left_pm (rit1)) #doctest: +NORMALIZE_WHITESPACE
    ('tuple', (('tuple', ('Type_Name_Type', 'BMT.Trap')), ('tuple', ('tuple', (('tuple', ('text-string', 'x')), ('tuple', ('number', 1))))))) ('tuple', (('tuple', ('Type_Name_Type', 'BMT.Rodent')), ('tuple', ('tuple', (('tuple', ('text-string', 'mighty_mouse')),)))))

    >>> show (RiT.r_query_s (right = t1, strict = True))
    [(('mighty_mouse', ), ('x', 1))]
    >>> show (RiT.r_query_s (trap = ("x", 2)))
    [(('axel', ), ('x', 2))]
    >>> show (RiT.r_query_s (trap = ("y", "1"), strict = True))
    [(('rutty_rat', ), ('y', 1))]
    >>> show (RiT.r_query_s (right = m))
    []
    >>> show (RiT.r_query_s (left = "Foxy_Fox", strict = True))
    []

    >>> show (RiT.r_query_s (left = m))
    [(('mighty_mouse', ), ('x', 1))]
    >>> show (RiT.r_query_s (rodent = "rutty_rat"))
    [(('rutty_rat', ), ('y', 1))]
    >>> show (RiT.r_query_s (left = ("axel", ), strict = True))
    [(('axel', ), ('x', 2))]
    >>> show (RiT.r_query_s (left = "Jimmy", strict = True))
    []

    >>> PoT.count
    4
    >>> show (PoT.r_query_s (left = p))
    [(('luke', 'lucky', ''), ('x', 1)), (('luke', 'lucky', ''), ('x', 2))]
    >>> show (PoT.r_query_s (person = ("dog",  "snoopy")))
    [(('dog', 'snoopy', ''), ('y', 1))]

    >>> PTL.count
    3
    >>> show (PTL.r_query_s (left = p, trap = t1))
    [(('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956))]
    >>> show (PTL.r_query_s (person = p, right = ("x", 2)))
    [(('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313))]
    >>> show (PTL.r_query_s (person = ("luke", "lucky"), trap = t3, strict = True))
    [(('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313))]
    >>> show (PTL.r_query_s (left = q, right = t1))
    []

    >>> show (PTL.r_query_s (left = p))
    [(('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956)), (('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313)), (('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313))]
    >>> show (PTL.query_s (location = l2))
    [(('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313)), (('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313))]
    >>> show (PTL.r_query_s (trap = ("y", "1")))
    [(('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313))]
    >>> show (PTL.r_query_s (person = ("Tan", "Tan")))
    []

    >>> show (PTL.r_query_s (left = p))
    [(('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956)), (('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313)), (('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313))]
    >>> show (PTL.r_query_s (right = ('x', 2)))
    [(('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313))]
    >>> show (PTL.r_query_s (location = l1))
    [(('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956))]
    >>> show (PTL.r_query_s (trap = t2, location = l2))
    [(('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313))]
    >>> show (PTL.r_query_s (right = ('y', 1), location = l1))
    []
    >>> show (PTL.r_query_s (left = p, right = ('x', 2), location = l2))
    [(('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313))]
    >>> show (PTL.r_query_s (person = p, trap = ('x', 2), location = l1))
    []
    >>> show (PTL.r_query_s (person = p, trap = ('x', 1), location = l1))
    [(('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956))]
    >>> show (PTL.r_query_s (left = ("Tan", "Tan")))
    []

    >>> show (PTL.links_of (p))
    [(('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956)), (('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313)), (('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313))]

    >>> t1
    BMT.Trap ('x', 1)
    >>> t1.all_links ()
    [BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 1)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956)), BMT.Rodent_in_Trap (('mighty_mouse', ), ('x', 1))]

    >>> list (scope)
    [BMT.Location (-16.268799, 48.189956), BMT.Location (-16.74077, 48.463313), BMT.Person ('luke', 'lucky', ''), BMT.Person ('dog', 'snoopy', ''), BMT.Person ('tin', 'tin', ''), BMT.Mouse ('mighty_mouse'), BMT.Beaver ('toothy_beaver'), BMT.Rat ('rutty_rat'), BMT.Rat ('axel'), BMT.Trap ('x', 1), BMT.Trap ('x', 2), BMT.Trap ('y', 1), BMT.Trap ('y', 2), BMT.Trap ('z', 3), BMT.Expected_Traptime (('rutty_rat', ), 9 days, 2:02:17.500000), BMT.Rodent_in_Trap (('mighty_mouse', ), ('x', 1)), BMT.Rodent_in_Trap (('rutty_rat', ), ('y', 1)), BMT.Rodent_in_Trap (('axel', ), ('x', 2)), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 1)), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 2)), BMT.Person_owns_Trap (('dog', 'snoopy', ''), ('y', 1)), BMT.Person_owns_Trap (('tin', 'tin', ''), ('y', 2)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313))]

    >>> len (list (scope))
    25

Changing objects and links
---------------------------

    >>> old_id = axel.pid
    >>> axel.all_links ()
    [BMT.Rodent_in_Trap (('axel', ), ('x', 2))]
    >>> axel.name = "betty"
    Traceback (most recent call last):
      ...
    AttributeError: Primary attribute `Rat.name` cannot be assigned.
    Use `set` or `set_raw` to change it.
    >>> axel.set (name = "betty")
    1
    >>> axel
    BMT.Rat ('betty')
    >>> axel.pid == old_id
    True
    >>> axel.all_links ()
    [BMT.Rodent_in_Trap (('betty', ), ('x', 2))]

    >>> print (p.as_code ())
    BMT.Person ('luke', 'lucky', '', )
    >>> with expect_except (MOM.Error.Invariants) :
    ...     p.set (middle_name = "zacharias")
    Invariants: Condition `AC_check_middle_name_length` : Value for middle_name must not be longer than 5 characters (length <= 5)
        length = 9 << len (middle_name)
        middle_name = 'zacharias'

    >>> m
    BMT.Mouse ('mighty_mouse')
    >>> prepr ((m.color, m.weight))
    ('', None)
    >>> print (m.as_code ())
    BMT.Mouse ('mighty_mouse', )
    >>> m.color = "white"
    >>> print (m.as_code ())
    BMT.Mouse ('mighty_mouse', color = 'white')
    >>> with expect_except (MOM.Error.Invariant) :
    ...     m.weight = 0
    Invariant: Condition `AC_check_weight_0` : weight > 0
        weight = 0.0
    >>> with expect_except (MOM.Error.Invariants) :
    ...     m.set (weight = -5.0)
    Invariants: Condition `AC_check_weight_0` : weight > 0
        weight = -5.0
    >>> m.weight = 10
    >>> print (m.as_code ())
    BMT.Mouse ('mighty_mouse', color = 'white', weight = 10)
    >>> m.set (color = "black", weight = 25.0)
    2
    >>> print (m.as_code ())
    BMT.Mouse ('mighty_mouse', color = 'black', weight = 25)
    >>> try :
    ...   m.set (weight = "'one ton'")
    ... except ValueError :
    ...   pass
    Error in `cooked` of `Float `weight`` for value `'one ton'` [('mighty_mouse')]
    >>> with expect_except (MOM.Error.Invariants) :
    ...     m.set_raw (weight = "one ton")
    Invariants: `Syntax error` for : `Float `weight``
         expected type  : 'Float'
         got      value : 'one ton'
    >>> m.set_raw (color = "yellow", weight = "6*7")
    2
    >>> prepr ((m.color, m.weight))
    ('yellow', 42)
    >>> print (m.as_code ())
    BMT.Mouse ('mighty_mouse', color = 'yellow', weight = 42)

    >>> csk = TFL.Sorted_By (Q.parent != None, Q.cid)
    >>> for c in m.changes ().order_by (csk).all () : ### ???
    ...     print (c)
    <Create BMT.Mouse ('mighty_mouse', 'BMT.Mouse'), new-values = {'last_cid' : '5'}>
    <Modify BMT.Mouse ('mighty_mouse', 'BMT.Mouse'), old-values = {'color' : '', 'last_cid' : '5'}, new-values = {'color' : 'white', 'last_cid' : '27'}>
    <Modify BMT.Mouse ('mighty_mouse', 'BMT.Mouse'), old-values = {'last_cid' : '27', 'weight' : ''}, new-values = {'last_cid' : '28', 'weight' : '10.0'}>
    <Modify BMT.Mouse ('mighty_mouse', 'BMT.Mouse'), old-values = {'color' : 'white', 'last_cid' : '28', 'weight' : '10.0'}, new-values = {'color' : 'black', 'last_cid' : '29', 'weight' : '25.0'}>
    <Modify BMT.Mouse ('mighty_mouse', 'BMT.Mouse'), old-values = {'color' : 'black', 'last_cid' : '29', 'weight' : '25.0'}, new-values = {'color' : 'yellow', 'last_cid' : '30', 'weight' : '42.0'}>

    >>> mm = m.copy ("Magic_Mouse")
    >>> for c in mm.changes ().order_by (csk).all () :
    ...     print (c)
    <Copy BMT.Mouse ('Magic_Mouse', 'BMT.Mouse'), new-values = {'last_cid' : '33'}>
        <Create BMT.Mouse ('Magic_Mouse', 'BMT.Mouse'), new-values = {'last_cid' : '31'}>
        <Modify BMT.Mouse ('Magic_Mouse', 'BMT.Mouse'), old-values = {'color' : '', 'last_cid' : '31', 'weight' : ''}, new-values = {'color' : 'yellow', 'last_cid' : '32', 'weight' : '42.0'}>
    <Create BMT.Mouse ('Magic_Mouse', 'BMT.Mouse'), new-values = {'last_cid' : '31'}>
    <Modify BMT.Mouse ('Magic_Mouse', 'BMT.Mouse'), old-values = {'color' : '', 'last_cid' : '31', 'weight' : ''}, new-values = {'color' : 'yellow', 'last_cid' : '32', 'weight' : '42.0'}>

    >>> print (l1.as_code ())
    BMT.Location (-16.268799, 48.189956, )
    >>> with expect_except (MOM.Error.Invariants) :
    ...     l1.set (lat =  91.5)
    Invariants: Condition `AC_check_lat_1` : -90.0 <= lat <= 90.0
        lat = 91.5
    >>> with expect_except (MOM.Error.Invariants) :
    ...     l1.set (lon = 270.0)
    Invariants: Condition `AC_check_lon_1` : -180.0 <= lon <= 180.0
        lon = 270.0
    >>> print (l1.as_code ())
    BMT.Location (-16.268799, 48.189956, )

    >>> rit = RiT.instance (m, t1)
    >>> print (rit.as_code ())
    BMT.Rodent_in_Trap (('mighty_mouse', ), ('x', 1), )
    >>> print (rit.rodent.as_code ())
    BMT.Mouse ('mighty_mouse', color = 'yellow', weight = 42)
    >>> print (rit.trap.as_code ())
    BMT.Trap ('x', 1, )
    >>> print (rit.is_g_correct ())
    True
    >>> rit.trap.max_weight = 20
    >>> print (rit.is_g_correct ())
    False
    >>> for err in rit.errors :
    ...     print (err)
    Condition `valid_weight` : Weight of `rodent` must not exceed `max_weight` of `trap`. (rodent.weight <= trap.max_weight)
        rodent = mighty_mouse
        rodent.weight = 42.0
        trap = x, 1
        trap.max_weight = 20.0

    >>> pot = PoT.instance (p, t1)
    >>> pot.price = float ("1.20")
    >>> print (pot.as_code ())
    BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 1), price = 1.2)

    >>> lcp = scope.query_changes (type_name = "BMT.Person").order_by (TFL.Sorted_By ("-cid")).first ()
    >>> prepr ((lcp.cid, lcp.epk))
    (21, ('tin', 'tin', '', 'BMT.Person'))
    >>> lcp
    <Create BMT.Person ('tin', 'tin', '', 'BMT.Person'), new-values = {'last_cid' : '21'}>

    >>> lct = scope.query_changes (type_name = "BMT.Trap").order_by (TFL.Sorted_By ("-cid")).first ()
    >>> prepr ((lct.cid, lct.epk))
    (34, ('x', '1', 'BMT.Trap'))
    >>> lct
    <Modify BMT.Trap ('x', '1', 'BMT.Trap'), old-values = {'last_cid' : '9', 'max_weight' : ''}, new-values = {'last_cid' : '34', 'max_weight' : '20.0'}>

Attribute queries
------------------

    >>> scope.BMT.Person.query_s (Q.last_name == Q.first_name).all ()
    [BMT.Person ('tin', 'tin', '')]
    >>> scope.BMT.Rodent.query_s (Q.weight != None).all ()
    [BMT.Mouse ('Magic_Mouse'), BMT.Mouse ('mighty_mouse')]
    >>> scope.BMT.Rodent.query_s (Q.weight != None).attr (Q.weight).all ()
    [42.0]
    >>> scope.BMT.Rodent.query_s (Q.weight == None).all ()
    [BMT.Rat ('betty'), BMT.Rat ('rutty_rat'), BMT.Beaver ('toothy_beaver')]
    >>> scope.BMT.Rodent.query_s (Q.weight > 0).all ()
    [BMT.Mouse ('Magic_Mouse'), BMT.Mouse ('mighty_mouse')]
    >>> scope.BMT.Trap.query_s (Q.serial_no > 1).all ()
    [BMT.Trap ('x', 2), BMT.Trap ('y', 2), BMT.Trap ('z', 3)]
    >>> scope.BMT.Trap.query_s (Q.serial_no < 2).all ()
    [BMT.Trap ('x', 1), BMT.Trap ('y', 1)]
    >>> scope.BMT.Trap.query_s (Q.serial_no %% 2).all ()
    [BMT.Trap ('x', 1), BMT.Trap ('y', 1), BMT.Trap ('z', 3)]

    >>> prepr ((tuple (scope.BMT.Rodent.query_s (Q.weight != None).attr (Q.weight, allow_duplicates = True))))
    (42, 42)
    >>> prepr ((tuple (scope.BMT.Rodent.query_s (Q.weight == None).attrs (Q.name, "color"))))
    (('betty', ''), ('rutty_rat', ''), ('toothy_beaver', ''))

    Use `query`, not `query_s`, to ensure that `Q.up_ex_q` is passed to DB
    (`query_s` returns a `TFL.Q_Result_Composite`).

    >>> sorted (scope.BMT.Trap.query (Q.serial_no %% 2).attr (Q.up_ex_q), key = TFL.Sorted_By ("+"))
    [None, 20.0]

    >>> tuple (scope.BMT.Trap.query (Q.max_weight != None).attr (Q.up_ex_q))
    (20.0,)

    >>> qr = scope.BMT.Trap.query (strict = 1).attrs ("name", "max_weight", "serial_no", "up_ex_q").all ()
    >>> sk = TFL.Sorted_By ("+")
    >>> prepr (sorted (qr, key = sk))
    [('x', None, 2, None), ('x', 20, 1, 20), ('y', None, 1, None), ('y', None, 2, None), ('z', None, 3, None)]

    >>> prepr ((sorted (scope.BMT.Trap.query (Q.up_ex_q > 0).attrs ("name", "max_weight", "serial_no", "up_ex_q"))))
    [('x', 20, 1, 20)]

Renaming objects and links
--------------------------

    >>> b.all_links ()
    []
    >>> rit.set (left = b)
    1
    >>> print (rit.as_code ())
    BMT.Rodent_in_Trap (('toothy_beaver', ), ('x', 1), )
    >>> b.all_links ()
    [BMT.Rodent_in_Trap (('toothy_beaver', ), ('x', 1))]
    >>> rit.rodent, rit.right
    (BMT.Beaver ('toothy_beaver'), BMT.Trap ('x', 1))

    >>> rit.set (rodent = m)
    1
    >>> print (rit.as_code ())
    BMT.Rodent_in_Trap (('mighty_mouse', ), ('x', 1), )

Deleting objects and links
--------------------------

    >>> scope.MOM.Link.query_s ().all ()
    [BMT.Rodent_in_Trap (('betty', ), ('x', 2)), BMT.Person_owns_Trap (('dog', 'snoopy', ''), ('y', 1)), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 1)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956)), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 2)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313)), BMT.Rodent_in_Trap (('mighty_mouse', ), ('x', 1)), BMT.Rodent_in_Trap (('rutty_rat', ), ('y', 1)), BMT.Expected_Traptime (('rutty_rat', ), 9 days, 2:02:17.500000), BMT.Person_owns_Trap (('tin', 'tin', ''), ('y', 2))]

    .. ### DBW-specific start

    >>> prepr (m.object_referring_attributes)
    defaultdict(<class 'builtins.list'>, {})

    >>> print (portable_repr (sorted (d.type_name for d in m.dependencies)))
    ['BMT.Rodent_in_Trap']
    >>> print (portable_repr (sorted (d.type_name for d in t1.dependencies))) ### 1
    ['BMT.Person_owns_Trap', 'BMT.Person_sets_Trap', 'BMT.Rodent_in_Trap']

    >>> m_id  = m.pid
    >>> t1_id = t1.pid
    >>> t2_id = t2.pid
    >>> show (scope.ems.all_links (m_id))
    [(('mighty_mouse', ), ('x', 1))]

    .. ### DBW-specific finish

    >>> show (t1.all_links ())
    [(('luke', 'lucky', ''), ('x', 1)), (('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956)), (('mighty_mouse', ), ('x', 1))]

    >>> t1.catch
    BMT.Mouse ('mighty_mouse')
    >>> m
    BMT.Mouse ('mighty_mouse')
    >>> m.destroy ()
    >>> t1.catch

    >>> show (t1.all_links ())
    [(('luke', 'lucky', ''), ('x', 1)), (('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956))]

    .. ### DBW-specific start

    >>> show (scope.ems.all_links (m_id))
    []

    >>> print (portable_repr (sorted (d.type_name for d in t1.dependencies))) ### 2
    ['BMT.Person_owns_Trap', 'BMT.Person_sets_Trap']

    .. ### DBW-specific finish

    >>> scope.MOM.Link.query_s ().count ()
    10
    >>> scope.MOM.Link.r_query_s ().all ()
    [BMT.Rodent_in_Trap (('betty', ), ('x', 2)), BMT.Person_owns_Trap (('dog', 'snoopy', ''), ('y', 1)), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 1)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 1), (-16.268799, 48.189956)), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 2)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313)), BMT.Rodent_in_Trap (('rutty_rat', ), ('y', 1)), BMT.Expected_Traptime (('rutty_rat', ), 9 days, 2:02:17.500000), BMT.Person_owns_Trap (('tin', 'tin', ''), ('y', 2))]

    >>> t1.destroy ()

    .. ### DBW-specific start

    >>> show (scope.ems.all_links (t1_id))
    []
    >>> show (scope.ems.all_links (t2_id))
    [(('luke', 'lucky', ''), ('x', 2)), (('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313)), (('betty', ), ('x', 2))]

    .. ### DBW-specific finish

    >>> scope.MOM.Link.query_s ().all ()
    [BMT.Rodent_in_Trap (('betty', ), ('x', 2)), BMT.Person_owns_Trap (('dog', 'snoopy', ''), ('y', 1)), BMT.Person_owns_Trap (('luke', 'lucky', ''), ('x', 2)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('x', 2), (-16.74077, 48.463313)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313)), BMT.Rodent_in_Trap (('rutty_rat', ), ('y', 1)), BMT.Expected_Traptime (('rutty_rat', ), 9 days, 2:02:17.500000), BMT.Person_owns_Trap (('tin', 'tin', ''), ('y', 2))]

    >>> t2.destroy ()
    >>> scope.MOM.Link.query_s ().all ()
    [BMT.Person_owns_Trap (('dog', 'snoopy', ''), ('y', 1)), BMT.Person_sets_Trap (('luke', 'lucky', ''), ('y', 1), (-16.74077, 48.463313)), BMT.Rodent_in_Trap (('rutty_rat', ), ('y', 1)), BMT.Expected_Traptime (('rutty_rat', ), 9 days, 2:02:17.500000), BMT.Person_owns_Trap (('tin', 'tin', ''), ('y', 2))]

    .. ### DBW-specific start

    >>> show (scope.ems.all_links (t2_id))
    []

    .. ### DBW-specific finish

Scope queries
--------------

    >>> for e in scope.i_incorrect () :
    ...     prepr (list (e.errors))

    >>> for e in scope.g_incorrect () :
    ...     prepr (list (str (x).replace (NL, " ") for x in e.errors))
    ['Condition `completely_defined` : All necessary attributes must be defined. Necessary attribute Float `weight` is not defined']
    ['Condition `completely_defined` : All necessary attributes must be defined. Necessary attribute Float `weight` is not defined']
    ['Condition `completely_defined` : All necessary attributes must be defined. Necessary attribute Float `weight` is not defined']

    >>> len (scope.uncommitted_changes)
    38
    >>> for c in scope.uncommitted_changes :
    ...     prepr (c)
    <Create BMT.Person ('luke', 'lucky', '', 'BMT.Person'), new-values = {'last_cid' : '1'}>
    <Create BMT.Person ('dog', 'snoopy', '', 'BMT.Person'), new-values = {'last_cid' : '2'}>
    <Create BMT.Location ('-16.268799', '48.189956', 'BMT.Location'), new-values = {'last_cid' : '3'}>
    <Create BMT.Location ('-16.74077', '48.463313', 'BMT.Location'), new-values = {'last_cid' : '4'}>
    <Create BMT.Mouse ('mighty_mouse', 'BMT.Mouse'), new-values = {'last_cid' : '5'}>
    <Create BMT.Beaver ('toothy_beaver', 'BMT.Beaver'), new-values = {'last_cid' : '6'}>
    <Create BMT.Rat ('rutty_rat', 'BMT.Rat'), new-values = {'last_cid' : '7'}>
    <Create BMT.Rat ('axel', 'BMT.Rat'), new-values = {'last_cid' : '8'}>
    <Create BMT.Trap ('x', '1', 'BMT.Trap'), new-values = {'last_cid' : '9'}>
    <Create BMT.Trap ('x', '2', 'BMT.Trap'), new-values = {'last_cid' : '10'}>
    <Create BMT.Trap ('y', '1', 'BMT.Trap'), new-values = {'last_cid' : '11'}>
    <Create BMT.Trap ('y', '2', 'BMT.Trap'), new-values = {'last_cid' : '12'}>
    <Create BMT.Trap ('z', '3', 'BMT.Trap'), new-values = {'last_cid' : '13'}>
    <Create BMT.Rodent_in_Trap (('mighty_mouse', 'BMT.Mouse'), ('x', '1', 'BMT.Trap'), 'BMT.Rodent_in_Trap'), new-values = {'last_cid' : '14'}>
    <Create BMT.Rodent_in_Trap (('rutty_rat', 'BMT.Rat'), ('y', '1', 'BMT.Trap'), 'BMT.Rodent_in_Trap'), new-values = {'last_cid' : '15'}>
    <Create BMT.Rodent_in_Trap (('axel', 'BMT.Rat'), ('x', '2', 'BMT.Trap'), 'BMT.Rodent_in_Trap'), new-values = {'last_cid' : '16'}>
    <Create BMT.Expected_Traptime (('rutty_rat', 'BMT.Rat'), '9d 02:02:17.500000', 'BMT.Expected_Traptime'), new-values = {'last_cid' : '17'}>
    <Create BMT.Person_owns_Trap (('luke', 'lucky', '', 'BMT.Person'), ('x', '1', 'BMT.Trap'), 'BMT.Person_owns_Trap'), new-values = {'last_cid' : '18'}>
    <Create BMT.Person_owns_Trap (('luke', 'lucky', '', 'BMT.Person'), ('x', '2', 'BMT.Trap'), 'BMT.Person_owns_Trap'), new-values = {'last_cid' : '19'}>
    <Create BMT.Person_owns_Trap (('dog', 'snoopy', '', 'BMT.Person'), ('y', '1', 'BMT.Trap'), 'BMT.Person_owns_Trap'), new-values = {'last_cid' : '20'}>
    <Create BMT.Person ('tin', 'tin', '', 'BMT.Person'), new-values = {'last_cid' : '21'}>
    <Create BMT.Person_owns_Trap (('tin', 'tin', '', 'BMT.Person'), ('y', '2', 'BMT.Trap'), 'BMT.Person_owns_Trap'), new-values = {'last_cid' : '22'}>
    <Create BMT.Person_sets_Trap (('luke', 'lucky', '', 'BMT.Person'), ('x', '1', 'BMT.Trap'), ('-16.268799', '48.189956', 'BMT.Location'), 'BMT.Person_sets_Trap'), new-values = {'last_cid' : '23'}>
    <Create BMT.Person_sets_Trap (('luke', 'lucky', '', 'BMT.Person'), ('x', '2', 'BMT.Trap'), ('-16.74077', '48.463313', 'BMT.Location'), 'BMT.Person_sets_Trap'), new-values = {'last_cid' : '24'}>
    <Create BMT.Person_sets_Trap (('luke', 'lucky', '', 'BMT.Person'), ('y', '1', 'BMT.Trap'), ('-16.74077', '48.463313', 'BMT.Location'), 'BMT.Person_sets_Trap'), new-values = {'last_cid' : '25'}>
    <Modify BMT.Rat ('betty', 'BMT.Rat'), old-values = {'last_cid' : '8', 'name' : 'axel'}, new-values = {'last_cid' : '26', 'name' : 'betty'}>
    <Modify BMT.Mouse ('mighty_mouse', 'BMT.Mouse'), old-values = {'color' : '', 'last_cid' : '5'}, new-values = {'color' : 'white', 'last_cid' : '27'}>
    <Modify BMT.Mouse ('mighty_mouse', 'BMT.Mouse'), old-values = {'last_cid' : '27', 'weight' : ''}, new-values = {'last_cid' : '28', 'weight' : '10.0'}>
    <Modify BMT.Mouse ('mighty_mouse', 'BMT.Mouse'), old-values = {'color' : 'white', 'last_cid' : '28', 'weight' : '10.0'}, new-values = {'color' : 'black', 'last_cid' : '29', 'weight' : '25.0'}>
    <Modify BMT.Mouse ('mighty_mouse', 'BMT.Mouse'), old-values = {'color' : 'black', 'last_cid' : '29', 'weight' : '25.0'}, new-values = {'color' : 'yellow', 'last_cid' : '30', 'weight' : '42.0'}>
    <Copy BMT.Mouse ('Magic_Mouse', 'BMT.Mouse'), new-values = {'last_cid' : '33'}>
        <Create BMT.Mouse ('Magic_Mouse', 'BMT.Mouse'), new-values = {'last_cid' : '31'}>
        <Modify BMT.Mouse ('Magic_Mouse', 'BMT.Mouse'), old-values = {'color' : '', 'last_cid' : '31', 'weight' : ''}, new-values = {'color' : 'yellow', 'last_cid' : '32', 'weight' : '42.0'}>
    <Modify BMT.Trap ('x', '1', 'BMT.Trap'), old-values = {'last_cid' : '9', 'max_weight' : ''}, new-values = {'last_cid' : '34', 'max_weight' : '20.0'}>
    <Modify BMT.Person_owns_Trap (('luke', 'lucky', '', 'BMT.Person'), ('x', '1', 'BMT.Trap'), 'BMT.Person_owns_Trap'), old-values = {'last_cid' : '18', 'price' : '42.0'}, new-values = {'last_cid' : '35', 'price' : '1.2'}>
    <Modify BMT.Rodent_in_Trap (('toothy_beaver', 'BMT.Beaver'), ('x', '1', 'BMT.Trap'), 'BMT.Rodent_in_Trap'), old-values = {'last_cid' : '14', 'left' : 5}, new-values = {'last_cid' : '36', 'left' : 6}>
    <Modify BMT.Rodent_in_Trap (('mighty_mouse', 'BMT.Mouse'), ('x', '1', 'BMT.Trap'), 'BMT.Rodent_in_Trap'), old-values = {'last_cid' : '36', 'left' : 6}, new-values = {'last_cid' : '37', 'left' : 5}>
    <Destroy BMT.Mouse ('mighty_mouse', 'BMT.Mouse'), old-values = {'color' : 'yellow', 'last_cid' : '30', 'weight' : '42.0'}>
        <Destroy BMT.Rodent_in_Trap (('mighty_mouse', 'BMT.Mouse'), ('x', '1', 'BMT.Trap'), 'BMT.Rodent_in_Trap'), old-values = {'last_cid' : '37'}>
    <Destroy BMT.Trap ('x', '1', 'BMT.Trap'), old-values = {'last_cid' : '34', 'max_weight' : '20.0'}>
        <Destroy BMT.Person_owns_Trap (('luke', 'lucky', '', 'BMT.Person'), ('x', '1', 'BMT.Trap'), 'BMT.Person_owns_Trap'), old-values = {'last_cid' : '35', 'price' : '1.2'}>
        <Destroy BMT.Person_sets_Trap (('luke', 'lucky', '', 'BMT.Person'), ('x', '1', 'BMT.Trap'), ('-16.268799', '48.189956', 'BMT.Location'), 'BMT.Person_sets_Trap'), old-values = {'last_cid' : '23'}>
    <Destroy BMT.Trap ('x', '2', 'BMT.Trap'), old-values = {'last_cid' : '10'}>
        <Destroy BMT.Person_owns_Trap (('luke', 'lucky', '', 'BMT.Person'), ('x', '2', 'BMT.Trap'), 'BMT.Person_owns_Trap'), old-values = {'last_cid' : '19'}>
        <Destroy BMT.Person_sets_Trap (('luke', 'lucky', '', 'BMT.Person'), ('x', '2', 'BMT.Trap'), ('-16.74077', '48.463313', 'BMT.Location'), 'BMT.Person_sets_Trap'), old-values = {'last_cid' : '24'}>
        <Destroy BMT.Rodent_in_Trap (('betty', 'BMT.Rat'), ('x', '2', 'BMT.Trap'), 'BMT.Rodent_in_Trap'), old-values = {'last_cid' : '16'}>
    >>> c = scope.uncommitted_changes [-2]
    >>> pckl = c.as_pickle (True)
    >>> cc = c.from_pickle (pckl)
    >>> cc
    <Destroy BMT.Trap ('x', '1', 'BMT.Trap'), old-values = {'last_cid' : '34', 'max_weight' : '20.0'}>
        <Destroy BMT.Person_owns_Trap (('luke', 'lucky', '', 'BMT.Person'), ('x', '1', 'BMT.Trap'), 'BMT.Person_owns_Trap'), old-values = {'last_cid' : '35', 'price' : '1.2'}>
        <Destroy BMT.Person_sets_Trap (('luke', 'lucky', '', 'BMT.Person'), ('x', '1', 'BMT.Trap'), ('-16.268799', '48.189956', 'BMT.Location'), 'BMT.Person_sets_Trap'), old-values = {'last_cid' : '23'}>
    >>> cc.children
    [<Destroy BMT.Person_owns_Trap (('luke', 'lucky', '', 'BMT.Person'), ('x', '1', 'BMT.Trap'), 'BMT.Person_owns_Trap'), old-values = {'last_cid' : '35', 'price' : '1.2'}>, <Destroy BMT.Person_sets_Trap (('luke', 'lucky', '', 'BMT.Person'), ('x', '1', 'BMT.Trap'), ('-16.268799', '48.189956', 'BMT.Location'), 'BMT.Person_sets_Trap'), old-values = {'last_cid' : '23'}>]
    >>> cc.children [0].parent is cc
    True
    >>> pckl = c.as_pickle ()
    >>> cc = c.from_pickle (pckl)
    >>> cc
    <Destroy BMT.Trap ('x', '1', 'BMT.Trap'), old-values = {'last_cid' : '34', 'max_weight' : '20.0'}>
    >>> cc.children
    []
    >>> scope.commit ()
    >>> len (scope.uncommitted_changes)
    0

Replaying changes
-----------------

    >>> scop2 = MOM.Scope.new (apt, %(db_scheme)s)
    >>> tuple (s.MOM.Id_Entity.count for s in (scope, scop2))
    (17, 0)
    >>> for c in scope.query_changes (Q.parent == None).order_by (Q.cid) :
    ...     c.redo (scop2)
    >>> tuple (s.MOM.Id_Entity.count for s in (scope, scop2))
    (17, 17)
    >>> prepr ((sorted (pyk.iteritems (scope.user_diff (scop2, ignore = ["last_cid"])))))
    []

    >>> t3.max_weight = 25
    >>> prepr ((sorted (pyk.iteritems (scope.user_diff (scop2, ignore = ["last_cid"])))))
    [(('BMT.Trap', ('y', '1', 'BMT.Trap')), {'max_weight' : ((25,), (None,))})]
    >>> scop2.BMT.Trap.instance (* t3.epk_raw, raw = True).set (max_weight = 42)
    1
    >>> prepr ((sorted (pyk.iteritems (scope.user_diff (scop2, ignore = ["last_cid"])))))
    [(('BMT.Trap', ('y', '1', 'BMT.Trap')), {'max_weight' : ((25,), (42,))})]
    >>> t3.destroy ()
    >>> for diff in sorted (pyk.iteritems (scop2.user_diff (scope, ignore = ["last_cid"]))) :
    ...     prepr (diff)
    (('BMT.Person_owns_Trap', (('dog', 'snoopy', '', 'BMT.Person'), ('y', '1', 'BMT.Trap'), 'BMT.Person_owns_Trap')), 'Present in Scope <hps://>, missing in Scope <hps://>')
    (('BMT.Person_sets_Trap', (('luke', 'lucky', '', 'BMT.Person'), ('y', '1', 'BMT.Trap'), ('-16.74077', '48.463313', 'BMT.Location'), 'BMT.Person_sets_Trap')), 'Present in Scope <hps://>, missing in Scope <hps://>')
    (('BMT.Rodent_in_Trap', (('rutty_rat', 'BMT.Rat'), ('y', '1', 'BMT.Trap'), 'BMT.Rodent_in_Trap')), 'Present in Scope <hps://>, missing in Scope <hps://>')
    (('BMT.Trap', ('y', '1', 'BMT.Trap')), 'Present in Scope <hps://>, missing in Scope <hps://>')
    >>> scope.user_equal (scop2)
    False

Saving and re-loading changes from a database
----------------------------------------------

    >>> db_path   = %(db_path)s
    >>> db_url    = "/".join ((%(db_scheme)s, %(db_path)s))
    >>> db_path_x = db_path + ".x"
    >>> if sos.path.exists (db_path) :
    ...     sos.remove (db_path)
    >>> if sos.path.exists (db_path_x) :
    ...     sos.rmdir (db_path_x, deletefiles = True)

    >>> scope.MOM.Id_Entity.count
    13
    >>> scop3 = scope.copy (apt, db_url)
    >>> tuple (s.MOM.Id_Entity.count for s in (scope, scop3))
    (13, 13)
    >>> sorted (pyk.iteritems (scop3.user_diff (scope)))
    []
    >>> all ((s.pid, s.as_pickle_cargo ()) == (t.pid, t.as_pickle_cargo ()) for (s, t) in zip (scope, scop3))
    True
    >>> scop3.destroy ()

    >>> scop4 = MOM.Scope.load (apt, db_url)
    >>> tuple (s.MOM.Id_Entity.count for s in (scope, scop4))
    (13, 13)
    >>> sorted (pyk.iteritems (scope.user_diff (scop4)))
    []
    >>> all ((s.pid, s.as_pickle_cargo ()) == (t.pid, t.as_pickle_cargo ()) for (s, t) in zip (scope, scop4))
    True
    >>> scop4.destroy ()

    >>> if sos.path.exists (db_path) : sos.remove (db_path)

Migrating all entities and the complete change history
------------------------------------------------------

    >>> scope.MOM.Id_Entity.count
    13
    >>> scope.query_changes ().count ()
    51
    >>> scop5 = scope.copy (apt, %(db_scheme)s)
    >>> tuple (s.MOM.Id_Entity.count for s in (scope, scop5))
    (13, 13)
    >>> tuple (s.query_changes ().count () for s in (scope, scop5))
    (51, 51)
    >>> all ((s.pid, s.as_pickle_cargo ()) == (t.pid, t.as_pickle_cargo ()) for (s, t) in zip (scope, scop5))
    True
    >>> all ((s.cid, s.pid) == (t.cid, t.pid) for (s, t) in zip (* (s.query_changes () for s in (scope, scop5))))
    True
    >>> scop5.destroy ()

Primary key attributes
-----------------------

    >>> with expect_except (MOM.Error.Invariants) :
    ...     scope.BMT.Trap ("", None)
    Invariants: Condition `name_not_empty` : The attribute name needs a non-empty value
        name = None
      Condition `serial_no_not_empty` : The attribute serial_no needs a non-empty value
        serial_no = None
    >>> with expect_except (MOM.Error.Invariants) :
    ...     scope.BMT.Trap ("ha", None)
    Invariants: Condition `serial_no_not_empty` : The attribute serial_no needs a non-empty value
        serial_no = None
    >>> with expect_except (MOM.Error.Invariants) :
    ...     scope.BMT.Trap ("", 0)
    Invariants: Condition `name_not_empty` : The attribute name needs a non-empty value
        name = None
    >>> with expect_except (MOM.Error.Invariants) :
    ...     scope.BMT.Trap (None, 0)
    Invariants: Condition `name_not_empty` : The attribute name needs a non-empty value
        name = None
    >>> with expect_except (MOM.Error.Invariants) :
    ...     scope.BMT.Trap ("ha", "", raw = True)
    Invariants: Condition `serial_no_not_empty` : The attribute serial_no needs a non-empty value
        serial_no = None
    >>> with expect_except (MOM.Error.Invariants) :
    ...     scope.BMT.Trap ("", "7", raw = True)
    Invariants: Condition `name_not_empty` : The attribute name needs a non-empty value
        name = None

Auto-updating attributes
-------------------------

An attribute can be updated automatically whenever the value of
another attribute changes. To define an auto-updating attribute,
specify the (names of the) attributes it depends on in
`auto_up_depends`.

    >>> t4.max_weight = 10
    >>> t4.max_weight, t4.serial_no
    (10.0, 2)
    >>> t4.up_ex, t4.up_ex_q
    (20.0, 20.0)
    >>> t4.max_weight = 5
    >>> t4.up_ex
    10.0
    >>> del t4.max_weight
    >>> t4.up_ex, t4.up_ex_q
    (None, None)

Unary links
-----------

    >>> sr = scope.BMT.Mouse ("Sick_Rodent")
    >>> osm = Ris (sr, scope.MOM.Date_Interval (start = "20100218", raw = True))
    >>> prepr (osm.as_code ())
    "BMT.Rodent_is_sick (('Sick_Rodent', ), ('2010-02-18', ), )"
    >>> osm.fever = 42
    >>> prepr (osm.as_code ())
    "BMT.Rodent_is_sick (('Sick_Rodent', ), ('2010-02-18', ), fever = 42)"
    >>> sorted (sr.sickness)
    [BMT.Rodent_is_sick (('Sick_Rodent', ), ('2010-02-18', ))]

Changing a composite primary attribute
--------------------------------------

    >>> old_epk = osm.epk
    >>> old_epk
    (BMT.Mouse ('Sick_Rodent'), MOM.Date_Interval ('2010-02-18'), 'BMT.Rodent_is_sick')
    >>> Ris.instance (* old_epk)
    BMT.Rodent_is_sick (('Sick_Rodent', ), ('2010-02-18', ))

    .. ### DBW-specific start

    >>> sorted (scope.ems._tables [osm.relevant_root.type_name])
    [(27, (datetime.date(2010, 2, 18), None))]

    .. ### DBW-specific finish

    >>> osm.sick_leave.set_raw (start = "2010-03-01")
    1
    >>> print (Ris.instance (* old_epk))
    None
    >>> osm.epk
    (BMT.Mouse ('Sick_Rodent'), MOM.Date_Interval ('2010-03-01'), 'BMT.Rodent_is_sick')
    >>> Ris.instance (* osm.epk)
    BMT.Rodent_is_sick (('Sick_Rodent', ), ('2010-03-01', ))

    .. ### DBW-specific start

    >>> sorted (scope.ems._tables [osm.relevant_root.type_name])
    [(27, (datetime.date(2010, 3, 1), None))]

    .. ### DBW-specific finish

Setting attribute values with Queries
-------------------------------------

    >>> t4.max_weight = 5.0

    >>> sorted (scope.BMT.Trap.query (Q.serial_no != None).attrs (Q.serial_no, Q.max_weight, Q.up_ex_q))
    [(2, 5.0, 10.0), (3, None, None)]

    >>> for x in scope.BMT.Trap.query_s (Q.serial_no != None):
    ...     _ = x.set (max_weight = 25)
    >>> sorted (scope.BMT.Trap.query (Q.serial_no != None).attrs (Q.serial_no, Q.max_weight, Q.up_ex_q))
    [(2, 25.0, 50.0), (3, 25.0, 75.0)]

    >>> scope.commit ()

    >>> sorted (scope.BMT.Trap.query (Q.serial_no != None).attrs (Q.serial_no, Q.max_weight, Q.up_ex_q))
    [(2, 25.0, 50.0), (3, 25.0, 75.0)]

Attributes with unit
------------------------

    >>> _ = p.set_raw (height = "1.57")
    >>> p.height
    1570

    ### the original raw value didn't specify a unit (default is meter)
    ### --> `raw_attr` doesn't show  unit
    >>> print (p.raw_attr ("height"))
    1.57

    >>> p.height += 20

    ### the raw value was changed due to the addition
    ### --> `raw_attr` shows the unit, which is still meter
    >>> print (p.raw_attr ("height"))
    1.59 m

    >>> _ = p.set_raw (height = "175 cm")
    >>> p.height
    1750

    ### an explicit unit was specified in the last assignment
    ### --> `raw_attr` shows that unit
    >>> print (p.raw_attr ("height"))
    175 cm


"""

def last_change (scope) :
    return scope.query_changes().order_by (TFL.Sorted_By ("-cid")).first ()
# end def last_change

__doc__ = doctest = dt_form % dict \
    ( import_DBW = "from _MOM._DBW._HPS.Manager import Manager"
    , import_EMS = "from _MOM._EMS.Hash         import Manager"
    , db_path    = "'/tmp/bmt_test.bmt'"
    , db_scheme  = "'hps://'"
    )
### __END__ GTW.__test__.MOM
