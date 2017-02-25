# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
# This module is part of the package GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.__test__.model
#
# Purpose
#    Helper function to create the App-Type for other tests
#
# Revision Dates
#    21-Apr-2010 (MG) Creation
#    27-Apr-2010 (CT) `MOM.Scaffold` factored
#    12-May-2010 (MG) `create_test_dict` added
#    19-May-2010 (CT) `create_test_dict` improved (use dict interpolation,
#                     parameters `bpt` (backends per test), `combiner`)
#    26-May-2010 (CT) Use anonymous account and database `test` for MySQL
#     1-Jul-2010 (MG) Support for loading a scope added
#     4-Aug-2010 (MG) Changed to new Scaffold structure
#    11-Aug-2010 (MG) `create_test_dict`: parameter `ignore` added
#    11-Aug-2010 (MG) `GTW_FULL_OBJECT_MODEL` added
#    12-Aug-2010 (MG) Fixture support handling added
#    16-Aug-2010 (MG) `scope` added to change the default of `verbose`
#    14-Jun-2011 (MG) `MYST` added to `Backend_Parameters`
#     9-Sep-2011 (CT) `from import_MOM import *` added
#    27-Jan-2012 (CT) Derive from `GTW.Werkzeug.Scaffold`
#    17-Apr-2012 (CT) Add `formatted`, `formatted_1`
#    26-Jul-2012 (CT) Adapt to use of `GTW.RST.TOP` instead of `GTW.NAV`
#    18-Sep-2012 (CT) Factor _GTW/__test__/Test_Command.py
#    13-Jun-2013 (CT) Remove `PNS_Aliases`
#    24-Jun-2013 (CT) Change `__main__` to consider `GTW_test_backends`
#    18-May-2016 (CT) Factor `create_app` in here (from _GTW.__test__.NAV)
#    ««revision-date»»···
#--

from   _GTW.__test__.Test_Command import *

import _GTW._OMP._Auth.import_Auth

if sos.environ.get ("GTW_FULL_OBJECT_MODEL", "True") != "False" :
    import _GTW._OMP._EVT.import_EVT
    import _GTW._OMP._EVT.UI_Spec

import _GTW._OMP._PAP.import_PAP
import _GTW._OMP._SRM.import_SRM
import _GTW._OMP._SWP.import_SWP

import _GTW._OMP._PAP.UI_Spec
import _GTW._OMP._SRM.UI_Spec
import _GTW._OMP._SWP.UI_Spec

class _GTW_Test_Command_ (GTW_Test_Command) :

    _rn_prefix            = "_GTW_Test"

    SALT                  = \
        b"ohQueiro7theG4vai9shi4oi9iedeethaeshooqu7oThi9Eecephaj"

    def fixtures (self, scope) :
        if sos.environ.get ("GTW_FIXTURES") :
            from _GTW.__test__.form_app import fixtures
            fixtures (scope)
    # end def fixtures

    def _nav_admin_groups (self) :
        RST = GTW.RST
        return \
            [ self.nav_admin_group
                ( "Personenverwaltung"
                , "Verwaltung von Personen und ihren Eigenschaften"
                , "GTW.OMP.PAP"
                )
            , self.nav_admin_group
                ( "Benutzerverwaltung"
                , "Verwaltung von Benutzer-Konten und Gruppen"
                , "GTW.OMP.Auth"
                , permission = RST.Is_Superuser ()
                )
            , self.nav_admin_group
                ( "Regattaverwaltung"
                , "Verwaltung von Regatten, Booten, "
                  "Teilnehmern und Ergebnissen"
                , "GTW.OMP.SRM"
                , show_aliases = True
                )
            , self.nav_admin_group
                ( "Webseitenverwaltung"
                , "Verwaltung der Webseiten"
                , "GTW.OMP.SWP", "GTW.OMP.EVT"
                , show_aliases = True
                )
            ]
    # end def _nav_admin_groups

_Command_  = _GTW_Test_Command_ # end class

Scaffold   = _Command_ ()

def create_app () :
    return Scaffold \
        ( [ "wsgi"
          , "-db_url",      "hps://"
          , "-db_name",     "test"
          , "-load_I18N",   "no"
          , "-Setup_Cache", "yes"
          ]
        )
# end def create_app

if __name__ == "__main__" :
    db_url = sos.environ.get ("GTW_test_backends", "sqlite:///auth.sqlite")
    if db_url in Scaffold.Backend_Parameters :
        db_url = Scaffold.Backend_Parameters [db_url].strip ("'")
    db_opt = "-db_url=%s" % db_url
    Scaffold (["create", db_opt])
    Scaffold (["shell", "-wsgi", db_opt])
### __END__ GTW.__test__.model
