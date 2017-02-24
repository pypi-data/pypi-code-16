# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# #*** <License> ************************************************************#
# This module is part of the package MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.Legacy_Lifter
#
# Purpose
#    Database legacy lifting during migration
#
# Revision Dates
#    19-Jan-2013 (MG) Creation
#    25-Jan-2013 (MG) Add filter code for old account passwort storage
#    29-Jan-2013 (MG) Lift `Type_Name` in pickle carge
#    30-Jan-2013 (MG) Add support for `removing` objects during legacy
#                     lifting
#    27-Nov-2013 (MG) Add part of the legacy lifting to the change objects as
#                     well (renaming of etypes)
#     8-Jan-2014 (CT) Refactor classes, add cache for `E_Type_Lifter`
#    26-Jan-2015 (CT) Use `M_Auto_Update_Combined`, not `M_Auto_Combine`,
#                     as metaclass
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from    _MOM                 import MOM
from    _TFL                 import TFL
from   _TFL.pyk              import pyk

import  _TFL._Meta.Object
import  _TFL.import_module
import  _TFL.sos             as     os

class _MOM_Legacy_Lifter_ \
          (TFL.Meta.BaM (object, metaclass = TFL.Meta.M_Auto_Update_Combined)) :
    """Base class for project specific legacy lifters"""

    _real_name               = "Legacy_Lifter"

    _attrs_to_update_combine = \
        ( "Type_Name_Renaming", "Type_Name_Lifter", "E_Type_Lifter")

    Type_Name_Renaming       = \
        { "Auth.Account_P" : "Auth.Account"
        }

    Type_Name_Lifter         = \
        { "Auth.Account"   : "_account_lifter"
        }

    E_Type_Lifter            = {}

    def __init__ (self, db_man) :
        self.db_man         = db_man
        self._et_lifter_map = {}
    # end def __init__

    def lift_change (self, chg_cls, chg_dct, children_pc) :
        type_name  = chg_dct ["type_name"]
        tn_changed = self.Type_Name_Renaming.get (type_name)
        if tn_changed :
            chg_dct ["type_name"] = tn_changed
            ### we changed the type name -> need to change it in the
            ### pickle cargo and the epk_pid, epk attributes as well
            for attr in "epk", "epk_pid" :
                chg_dct [attr] = chg_dct [attr] [:-1] + (tn_changed, )
            chg_dct ["pickle_cargo"] = \
                (tn_changed, ) + chg_dct ["pickle_cargo"] [1:]
        return chg_cls, chg_dct, children_pc
    # end def lift_change

    def lift_entity (self, type_name, pc, pid) :
        tn_changed = self.Type_Name_Renaming.get (type_name)
        if tn_changed :
            type_name = tn_changed
            if "Type_Name" in pc :
                pc ["Type_Name"] = [type_name]
        tn_lifter_name = self.Type_Name_Lifter.get (type_name)
        if tn_lifter_name :
            tn_lifter = getattr (self, tn_lifter_name)
            type_name, pc, pid = tn_lifter (type_name, pc, pid)
        if type_name and self.E_Type_Lifter :
            for et_lifter in self._et_lifters (type_name) :
                type_name, pc, pid = et_lifter (type_name, pc, pid)
        return type_name, pc, pid
    # end def lift_entity

    def _account_lifter (self, type_name, pc, pid) :
        if ("salt" in pc) and ("ph_name" not in pc) :
            salt            = pc.pop ("salt") [0]
            pc ["password"] = ["%s::%s" % (salt, pc ["password"] [0])]
            pc ["ph_name"]  = ["sha224"]
        return type_name, pc, pid
    # end def _account_lifter

    def _et_lifters (self, type_name) :
        map = self._et_lifter_map
        try :
            result = map [type_name]
        except KeyError :
            result = map [type_name] = []
            apt    = self.db_man.app_type
            pc_et  = apt [type_name]
            for tn, et_lifter_name in pyk.iteritems (self.E_Type_Lifter) :
                et = apt [tn]
                if issubclass (pc_et, et) :
                    result.append (getattr (self, et_lifter_name))
            result.sort (key = TFL.Getter.i_rank)
        return result
    # end def _et_lifters

Legacy_Lifter = _MOM_Legacy_Lifter_ # end class

class Legacy_Lifter_Wrapper (TFL.Meta.Object) :
    """Wrapper around a `db_man` and a project specific legacy lifter"""

    def __init__ (self, db_man, module_name) :
        LL_Class           = TFL.import_module (module_name).Legacy_Lifter
        self.legacy_lifter = LL_Class (db_man)
    # end def __init__

    def entity_iter (self, db_iter) :
        lifter = self.legacy_lifter
        for type_name, pc, pid in db_iter :
            type_name, pc, pid = lifter.lift_entity (type_name, pc, pid)
            if type_name is not None :
                yield type_name, pc, pid
    # end def entity_iter

    def change_iter (self, db_iter) :
        lifter = self.legacy_lifter
        for chg_cls, chg_dct, children_pc in db_iter :
            yield lifter.lift_change (chg_cls, chg_dct, children_pc)
    # end def change_iter

# end class Legacy_Lifter_Wrapper

if __name__ != "__main__" :
    MOM._Export ("*")
### __END__ MOM.Legacy_Lifter
