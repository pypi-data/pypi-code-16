# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
# This module is part of the package GTW.OMP.Auth.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.Auth.Account_Handling
#
# Purpose
#    Define the links used during the create/modify process for accounts
#
# Revision Dates
#    18-Feb-2010 (MG) Creation
#    19-Feb-2010 (MG) `Account_Token_Manager` added
#    19-Feb-2010 (MG) Reorganized
#    20-Feb-2010 (MG) Account management functions added
#    20-Feb-2010 (MG) Expiration of actions added
#    14-Oct-2010 (CT) `Init_Only_Mixin` added to `token`
#    14-Oct-2010 (CT) `Account_Pasword_Reset.password` changed to `A_String`
#    15-Dec-2010 (CT) s/Account_Pasword_Reset/Account_Password_Reset/
#    15-Dec-2010 (CT) `Account_Password_Reset.handle` changed to lift
#                     `suspended`
#    22-Dec-2010 (CT) `_Account_Action_.electric` redefined to `True`
#    20-Jul-2011 (CT) Use `datetime.utcnow` instead of `datetime.now`
#    16-Aug-2012 (MG) Add `description` attribute to Action links
#    28-Jan-2013 (CT) Fix spelling of `Action_Expired`
#    10-May-2013 (CT) Add `_Account_Action_.show_in_ui_T = False`
#    13-May-2013 (CT) Replace `auto_cache` by `link_ref_attr_name`
#    11-Jun-2015 (CT) Move `description.default` to `Account_EMail_Verification`
#     8-Oct-2015 (CT) Change `Account_Token_Manager.__call__` to allow `()`
#                     (`example` does that and triggers a warning otherwise)
#    ««revision-date»»···
#--

from   _MOM.import_MOM        import *
from   _GTW                   import GTW

from   _GTW._OMP._Auth        import Auth
import _GTW._OMP._Auth.Entity
import _GTW._OMP._Auth.Account

from   _TFL.I18N              import _, _T, _Tn
import  uuid
import  datetime

class Action_Expired (Exception) : pass

_Ancestor_Essence = Auth.Link1

class _Account_Action_ (_Ancestor_Essence) :
    """Base class for different actions for a account."""

    is_partial    = True
    show_in_ui_T  = False

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :
            """Account which this action is bound to."""

            role_type     = Auth.Account

        # end class left

        class electric (_Ancestor.electric) :

            kind               = Attr.Const
            default            = False

        # end class electric

    # end class _Attributes

# end class _Account_Action_

_Ancestor_Essence = _Account_Action_

class Account_Activation (_Ancestor_Essence) :
    """Activation of the account"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :
            """Account which this action is bound to."""

            max_links          = 1
            link_ref_attr_name = "activation"

        # end class left

    # end class _Attributes

# end class Account_Activation

_Ancestor_Essence = _Account_Action_

class Account_Password_Change_Required (_Ancestor_Essence) :
    """The password of the linked account must be changed after the next
       login.
    """

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :
            """Account which this action is bound to."""

            max_links          = 1
            link_ref_attr_name = "password_change_required"

        # end class left

    # end class _Attributes

# end class Account_Password_Change_Required

_Ancestor_Essence = _Account_Action_

class Account_Token_Manager (_Ancestor_Essence.M_E_Type.Manager) :
    """E-Type manager for token based account actions"""

    def __call__ (self, account = None, expires = None, ** kw) :
        ### `account` is None in case of `Account_Token_Manager.example`
        if account is not None :
            token = uuid.uuid4 ().hex
            if not expires :
                etype   = self._etype
                expires = \
                    datetime.datetime.utcnow () + etype.expire_duration_default
            return self.__super.__call__ \
                (account, token = token, expires = expires, ** kw)
    # end def __call__

# end class Account_Token_Manager

class _Account_Token_Action_ (_Ancestor_Essence) :
    """Base class for account actions which have an token to identify the
       action without the account.
    """

    is_partial              = True
    Manager                 = Account_Token_Manager

    expire_duration_default = datetime.timedelta (hours = 1)


    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class token (A_String) :
            """Unique token which identifies this action."""

            kind          = Attr.Primary
            Kind_Mixins   = (Attr.Init_Only_Mixin, )

        # end class token

        class description (A_String) :

            kind               = Attr.Const
            max_length         = 100

        # end class description

        class expires (A_Date_Time) :
            """Exipre time of this action"""

            kind          = Attr.Necessary

        # end class expires

    # end class _Attributes

    def handle (self, nav = None) :
        if self.expires < datetime.datetime.utcnow () :
            raise Action_Expired
    # end def handle

# end class _Account_Token_Action_

_Ancestor_Essence = _Account_Token_Action_

class Account_EMail_Verification (_Ancestor_Essence) :
    """Pending email verification."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class description (_Ancestor.description) :

            default            = "Email verification successful."

        # end class description

        class new_email (A_Email) :
            """The new email address for the linked account."""

            kind               = Attr.Optional

        # end class new_email

    # end class _Attributes

    def handle (self, nav = None) :
        self.__super.handle ()
        account = self.account
        next    = "/"
        if self.new_email :
            ### this the verification of a email change request
            account.set (name = self.new_email, suspended = False)
        else :
            account.set (suspended = False)
        for l in self.home_scope.GTW.OMP.Auth.Account_EMail_Verification.query \
                (account = account) :
            l.destroy ()
        return next
    # end def handle

# end class Account_EMail_Verification

_Ancestor_Essence = _Account_Token_Action_

class Account_Password_Reset (_Ancestor_Essence) :
    """A password reset is pending for the linked account."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class password (A_String) :
            """The temporary password."""

            kind               = Attr.Necessary

        # end class password

    # end class _Attributes

    def handle (self, nav = None) :
        self.__super.handle ()
        account = self.account
        account.change_password (self.password, False)
        account.set (suspended = False)
        for l in self.home_scope.GTW.OMP.Auth.Account_Password_Reset.query \
                (account = account) :
            l.destroy ()
        if nav :
            return nav.href_reset_password (account)
    # end def handle

# end class Account_Password_Reset

if __name__ != "__main__" :
    GTW.OMP.Auth._Export ("*")
### __END__ GTW.OMP.Auth.Account_Handling
