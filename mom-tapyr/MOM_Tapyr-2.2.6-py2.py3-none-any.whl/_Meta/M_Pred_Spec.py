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
#    MOM.Meta.M_Pred_Spec
#
# Purpose
#    Meta class for MOM.Pred.Spec classes
#
# Revision Dates
#    29-Sep-2009 (CT) Creation (factored from TOM.Meta.M_Pred_Spec)
#    15-Apr-2012 (CT) Adapted to changes of `MOM.Error`
#    ««revision-date»»···
#--

from   _MOM                import MOM

import _MOM._Meta.M_Prop_Spec
import _MOM.Error

class M_Pred_Spec (MOM.Meta.M_Prop_Spec) :
    """Meta class for `MOM.Pred.Spec`. It gathers all (including all
       inherited) members of `Spec` which are derived from `_Condition_` and
       puts them into the class attribute `_names`.

       Setting a member to `None` in a derived `Spec` will remove the
       predicate from the `Spec`.
    """

    def _m_inconsistent_prop (cls, n, v, _names, dict) :
        return MOM.Error.Inconsistent_Predicate \
            ( "%s: Predicate `%s = %r` of %s clashes with %s"
            % (dict ["__module__"], n, v, dict ["__name__"], _names [n])
            )
    # end def _m_inconsistent_prop

# end class M_Pred_Spec

### «text» ### start of documentation
__doc__ = """

"""

if __name__ != "__main__" :
    MOM.Meta._Export ("*")
### __END__ MOM.Meta.M_Pred_Spec
