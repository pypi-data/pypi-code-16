# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Mag. Christian Tanzer All rights reserved
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
#    GTW.__test__.Entity_Reload
#
# Purpose
#    Test entity reloading after a scope.commit and changes in a different
#    process
#
# Revision Dates
#    15-Jun-2012 (MG) Creation
#    27-Jun-2012 (CT) Test `b1.name` before querying for `b3`
#    ««revision-date»»···
#--

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> SRM = scope.SRM

    >>> opti  = SRM.Boat_Class (name = "Optimist", max_crew = 1)
    >>> laser = SRM.Boat_Class (name = "Laser", max_crew = 1)
    >>> b1    = SRM.Boat (u'Optimist', u"1107", u"AUT", raw = True) ### 1
    >>> b2    = SRM.Boat (u"Laser", "42", None, "OE", raw = True)

    >>> laser.max_crew ### before commit
    1
    >>> prepr (b1.name) ### before commit
    ''

    >>> scope.commit  ()
    >>> modify_scope (%(p1)s, %(n1)s)

    >>> laser.max_crew ### after change
    2
    >>> prepr (b1.name) ### after change
    'My Boat'

    >>> b3 = scope.SRM.Boat.query (nation = u"AUT").one ()
    >>> b3 is b1
    True


"""

from _GTW.__test__.model import *
from multiprocessing     import Process
_Ancestor_Essence = GTW.OMP.SRM.Boat

Scaffold.Backend_Parameters ["SQL"] = "'sqlite:///test.sqlite'"
Scaffold.Backend_Parameters ["sq"]  = "'sqlite:///test.sqlite'"

def _modify_scope (* args) :
    scope          = Scaffold.scope (* args, create = False, verbose = False)
    laser          = scope.SRM.Boat_Class.query (name = u"laser").one ()
    laser.max_crew = 2
    boat           = scope.SRM.Boat.query (nation = u"AUT").one ()
    boat.name      = "My Boat"
    scope.commit  ()
    scope.destroy ()
# end def _modify_scope

def modify_scope (* args) :
    if 1 :
        p = Process   (target = _modify_scope, args = args)
        p.start       ()
        p.join        ()
    else :
        _modify_scope (* args)
# end def modify_scope

__test__ = Scaffold.create_test_dict (_test_code, ignore = "HPS")

### __END__ GTW.__test__.Entity_Reload
