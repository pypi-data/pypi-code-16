# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.SWP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.SWP.Gallery
#
# Purpose
#    Model a gallery of pictures
#
# Revision Dates
#    22-Mar-2010 (CT) Creation
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    17-Feb-2014 (CT) Set `Gallery.directory.do_check` to `False`
#    ««revision-date»»···
#--

from   __future__               import unicode_literals

from   _MOM.import_MOM          import *
from   _GTW                     import GTW

import _GTW._OMP._SWP.Entity

from   _TFL.I18N                import _, _T, _Tn

_Ancestor_Essence = GTW.OMP.SWP.Object_PN

class Gallery (_Ancestor_Essence) :
    """Model a gallery of pictures"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class directory (A_Dirname) :
            """Directory where pictures of gallery are stored."""

            kind               = Attr.Necessary

            ### `directory` is relative to the apache root
            ### existence check in filesystem would fail
            do_check           = False

        # end class directory

    # end class _Attributes

# end class Gallery

if __name__ != "__main__" :
    GTW.OMP.SWP._Export ("*")
### __END__ GTW.OMP.SWP.Gallery
