# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.Document
#
# Purpose
#    Model a document linked to some other entity
#
# Revision Dates
#     6-Mar-2012 (CT) Creation
#    10-Feb-2014 (CT) Improve attribute docstrings
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _MOM.import_MOM        import *

from   _TFL.I18N              import _

_Ancestor_Essence = MOM.Link1

class Document (_Ancestor_Essence) :
    """Model a document linked to some other entity."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Entity the %(ui_name.lower ())s applies to."""

            role_type          = MOM.Id_Entity
            role_name          = "entity"

        # end class left

        class url (A_Url) :
            """Location of %(ui_name.lower ())s."""

            kind               = Attr.Primary
            completer          = Attr.Completer_Spec  (4, Attr.Selector.primary)

        # end class url

        class type (A_String) :
            """Type of %(ui_name.lower ())s (e.g., picture, user manual)."""

            kind               = Attr.Primary_Optional
            max_length         = 24
            ignore_case        = True
            completer          = Attr.Completer_Spec (1)

        # end class type

        ### Non-primary attributes

        class desc (A_String) :
            """Description of %(ui_name.lower ())s."""

            kind               = Attr.Optional
            max_length         = 160
            ui_name            = _("Description")

            completer          = Attr.Completer_Spec  (1)

        # end class description

    # end class _Attributes

# end class Document

if __name__ != "__main__" :
    MOM._Export ("*")
### __END__ MOM.Document
