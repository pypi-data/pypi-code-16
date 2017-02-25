# -*- coding: utf-8 -*-
# Copyright (C) 2010-2017 Martin Glueck All rights reserved
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
#    GTW.__test__.MOM_SAW
#
# Purpose
#    Proxy for the MOM.DBW.SAW.__doc__ tests
#
# Revision Dates
#    12-Feb-2010 (MG) Creation
#    16-Feb-2010 (MG) Test for database migration added
#    27-Sep-2012 (CT) Move test code from `MOM.DBW.SAW.__doc__` in here
#    24-Feb-2017 (CT) Import `MOM.Inspect`, not `MOM.inspect`
#    ««revision-date»»···
#--

from   __future__  import print_function, unicode_literals

from   _GTW.__test__.MOM import \
    ( dt_form, MOM, BMT, show, NL, sos, last_change
    , portable_repr, prepr, pyk
    )
from   _MOM.Inspect import show_children, show_ref_map, show_ref_maps

from   _TFL.formatted_repr        import formatted_repr as formatted
from   _TFL.Regexp                import Dict_Replacer, re

filter_dbw_pat = re.compile \
    (  "\#\#\#\sDBW-specific\sstart.+?\#\#\#\sDBW-specific\sfinish"
    , re.DOTALL | re.X | re.MULTILINE
    )

fixer = Dict_Replacer ({"__Hash" : "__SAW", "__HPS": "__SAW", "hps://" : "sqlite://"})

__doc__ = fixer \
    ( filter_dbw_pat.sub ("", dt_form)
    % dict
        ( import_DBW = "from _MOM._DBW._SAW.Manager import Manager"
        , import_EMS = "from _MOM._EMS.SAW          import Manager"
        , db_path    = "'test.sqlite'"
        , db_scheme  = "'sqlite://'"
        )
    )

_db_mig_test = """
>>> from _MOM._DBW._HPS.Manager import Manager as DBW_HPS
>>> from _MOM._EMS.Hash         import Manager as EMS_HPS
>>> from _MOM._DBW._SAW.Manager import Manager as DBW_SAW
>>> from _MOM._EMS.SAW          import Manager as EMS_SAW

>>> apt_gen = MOM.App_Type    (u"BMT_DBM", BMT)
>>> apt_sas = apt_gen.Derived (EMS_SAW, DBW_SAW)
>>> apt_hps = apt_gen.Derived (EMS_HPS, DBW_HPS)
>>> apt_sas is apt_hps
False
>>> apt_sas.parent is apt_hps.parent
True
>>> db_path_old  = "scope_old.sqlite"
>>> db_path_new  = "scope_new.sqlite"
>>> hps_filename = "scope_hps"
>>> hps_path     = "%s.bmt" % (hps_filename, )
>>> hps_url      = "hps:///%s" % (hps_path, )
>>> remove (db_path_old)
>>> remove (db_path_new)
>>> remove (hps_path)
>>> remove (hps_path + ".X", True)
>>> scope_1 = MOM.Scope.new          (apt_sas, "sqlite:///%s" % (db_path_old, ))
>>> m1 = scope_1.BMT.Mouse           ("Mouse_1")
>>> m2 = scope_1.BMT.Mouse           ("Mouse_2")
>>> m3 = scope_1.BMT.Mouse           ("Mouse_3")
>>> r1 = scope_1.BMT.Rat             ("Rat_1")
>>> t1 = scope_1.BMT.Trap            ("Brand", 1)
>>> t2 = scope_1.BMT.Trap            ("Brand", 2)
>>> t3 = scope_1.BMT.Trap            ("Brand", 3)
>>> t4 = scope_1.BMT.Trap            ("Brand", 4)
>>> rit = scope_1.BMT.Rodent_in_Trap (m1, t1)
>>> rit = scope_1.BMT.Rodent_in_Trap (m2, t2)
>>> rit = scope_1.BMT.Rodent_in_Trap (m3, t3)
>>> rit = scope_1.BMT.Rodent_in_Trap (r1, t4)
>>> scope_1.commit                   ()
>>> scope_1.destroy                  ()

Now, we load the `old` database and save it as a HPS
>>> scope_1 = MOM.Scope.load         (apt_sas, "sqlite:///%s" % (db_path_old, ))
>>> scope_2 = scope_1.copy           (apt_hps, hps_url)
>>> scope_1.destroy                  ()
>>> scope_2.destroy                  ()

Here is the point where we upgrade the object model and load the HPS database
again to perform the migration
>>> scope_2 = MOM.Scope.load         (apt_hps, hps_url)
>>> scope_3 = scope_2.copy           (apt_sas, "sqlite:///%s" % (db_path_new, ))
>>> scope_2.destroy                  ()
>>> scope_3.destroy                  ()

Now we load the old and the new SAW based scopes and compare them
>>> scope_1 = MOM.Scope.load         (apt_sas, "sqlite:///%s" % (db_path_old, ))
>>> scope_3 = MOM.Scope.load         (apt_sas, "sqlite:///%s" % (db_path_new, ))
>>> tuple (s.MOM.Id_Entity.count for s in (scope_1, scope_3))
(12, 12)
>>> sorted (pyk.iteritems (scope_1.user_diff (scope_3, ignore = ["last_cid"])))
[]
>>> scope_1.destroy ()
>>> scope_3.destroy ()

>>> remove          (db_path_old)
>>> remove          (db_path_new)
>>> remove          (hps_filename + ".bak")
>>> remove          (hps_path)
>>> remove          (hps_path + ".X", True)

"""

__test__ = dict (test_db_migration = _db_mig_test)

def remove (file, is_dir = False) :
    if sos.path.exists (file) :
        if is_dir :
            sos.rmdir  (file, deletefiles = True)
        else :
            sos.unlink (file)
# end def remove

### __END__ GTW.__test__.MOM_SAW
