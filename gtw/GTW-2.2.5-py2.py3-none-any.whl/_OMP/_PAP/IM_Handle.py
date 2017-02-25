# -*- coding: utf-8 -*-
# Copyright (C) 2012 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.PAP.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.PAP.IM_Handle
#
# Purpose
#    Model a IM (instant messaging) handle
#
# Revision Dates
#     9-Nov-2012 (CT) Creation
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _MOM.import_MOM        import *
from   _GTW                   import GTW
from   _GTW._OMP._PAP         import PAP
from   _TFL.I18N              import _

import _GTW._OMP._PAP.Property

class A_IM_Protocol (A_Enum) :
    """Instant messaging protocol"""

    example    = "XMPP"
    typ        = "im_protocol"

    C_Type     = A_String
    max_length = 16

    Table      = dict \
        ( ICQ         = _("First internet-wide instant messaging service")
        , IRC         = _("Internet relay chat")
        , XMPP        = _
            ( "Extensible messaging and presence protocol; used by Jabber "
              "and Google Talk"
            )
        )

# end class A_IM_Protocol

_Ancestor_Essence = PAP.Property

class _PAP_IM_Handle_ (_Ancestor_Essence) :
    """Handle of a subject for an instant messaging system"""

    _real_name = "IM_Handle"

    ui_display_sep = "://"

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class protocol (A_IM_Protocol) :
            """IM Protocol of handle"""

            kind               = Attr.Primary

        # end class protocol

        class address (A_String) :
            """IM address (excluding protocol)"""

            kind               = Attr.Primary
            example            = "john.doe@example.com"
            ignore_case        = True
            max_length         = 80
            completer          = Attr.Completer_Spec  (2, Attr.Selector.primary)

        # end class address

    # end class _Attributes

IM_Handle = _PAP_IM_Handle_ # end class

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.IM_Handle
