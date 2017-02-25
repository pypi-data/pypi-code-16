# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg. martin@mangari.org
# ****************************************************************************
# This package is part of the package GTW.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.Auth.Account
#
# Purpose
#    Model an user account
#
# Revision Dates
#    13-Jan-2010 (MG) Creation
#    14-Jan-2010 (CT) `password` defined as `Required` instead of `Primary`
#    14-Jan-2010 (CT) s/Password_Account/Account_P/g
#    16-Jan-2010 (CT) Derive from `Auth.Object` (thus s/usernamer/name/)
#     3-Feb-2010 (MG) Password hashing added
#    18-Feb-2010 (MG) `Account_P`: `salt` added as class attribute
#    19-Feb-2010 (MG) `Account_P_Manager` added, `Account` is no longer a
#                     `Named_Object` due to restrictions of the name (could
#                     not be an email address)
#    19-Feb-2010 (MG) Change password handling added
#    19-Feb-2010 (MG) `Account`: new attributes `enabled` and `suspended`
#                     added, kind `active` changed to `Attr.Query`
#    19-Feb-2010 (MG) `reset_password` implemented
#    19-Feb-2010 (MG) Account activation added
#    20-Feb-2010 (MG) Account management functions added
#    26-Feb-2010 (CT) `authenticated` defined as alias for `active`
#    26-Feb-2010 (CT) `kind` of `suspended`, `password`, and `salt` changed
#                     to `Internal` (set by the application, not the user)
#    18-May-2010 (CT) `Account_P_Manager.__call__` replaced by
#                     `Account_P_Manager.create_new_account_x`
#    14-Oct-2010 (CT) `Init_Only_Mixin` added to `salt`
#    15-Dec-2010 (CT) s/Account_Pasword_Reset/Account_Password_Reset/
#    15-Dec-2010 (CT) `Account_P_Manager.reset_password` fixed
#    22-Dec-2010 (CT) `_Auth_Account_.electric`, `.is_partial` and
#                     `.is_relevant` redefined to `True`
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    29-Mar-2012 (CT) Redefine `Account_Anonymous.x_locked` instead of
#                     `.electric`
#     7-Aug-2012 (CT) Set `Account_Anonymous.electric` to True
#    24-Sep-2012 (CT) Rename `Account` to `_Account_`, `Account_P` to `Account`
#     9-Oct-2012 (CT) Improve attribute docstrings
#     6-Dec-2012 (CT) Remove `Entity_created_by_Person`
#     5-Jan-2013 (CT) Use `TFL.Password_Hasher`, not homegrown code
#     6-Jan-2013 (CT) Increase `password.max_length` to 120 (from 60)
#     5-May-2013 (CT) Add warning about unknown `hasher` to `verify_password`
#     6-May-2013 (CT) Add missing `import logging` (forgot yesterday)
#     6-May-2013 (CT) Add `sys.path` to, raise KeyError in, `verify_password`
#     6-May-2013 (CT) Factor `unknown_hasher`, use it in `password_hash`;
#                     fix `ph_name.computed_default`
#    10-May-2013 (CT) Set `Account_Anonymous.show_in_ui = False`
#    26-May-2013 (CT) Add `Account_Manager.apply_migration`, `.migration`
#    27-May-2013 (CT) Make `create_new_account_x` argument `password` optional
#     5-Jun-2013 (CT) Set `password.q_able` to `False`
#    16-Jun-2015 (CT) Change `random_password` to start with letter or digit
#    29-Nov-2016 (CT) Remove `Account_Anonymous`
#    29-Nov-2016 (CT) Remove `_Account_.is_relevant`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _MOM.import_MOM        import *
from   _GTW                   import GTW

from   _GTW._OMP._Auth        import Auth
import _GTW._OMP._Auth.Entity

from   _TFL.pyk               import pyk

import _TFL.Password_Hasher

import logging
import sys

_Ancestor_Essence = Auth.Object

class _Auth_Account_ (_Ancestor_Essence) :
    """Model an user account."""

    _real_name  = "_Account_"

    is_partial  = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class name (A_Email) :
            """Email that serves as user name for this account"""

            kind               = Attr.Primary

        # end class name

        class active (A_Boolean) :
            """Specifies if this account is currently active."""

            kind               = Attr.Query
            auto_up_depends    = ("suspended", "enabled")
            query              = (Q.suspended != True) & (Q.enabled == True)

        # end class active

        class enabled (A_Boolean) :
            """Specifies if this account is currently enabled, i.e.,
               the user can login.
            """

            kind               = Attr.Optional
            default            = False

        # end class enabled

        class superuser (A_Boolean) :
            """Specifies if this account has super-user permissions."""

            kind               = Attr.Optional
            default            = False

        # end class superuser

        class suspended (A_Boolean) :
            """Specifies if this account is currently suspended
               (due to a pending action).
            """

            kind               = Attr.Internal
            default            = True

        # end class suspended

    # end class _Attributes

    authenticated = TFL.Meta.Alias_Property ("active")

_Account_ = _Auth_Account_ # end class _Auth_Account_

_Ancestor_Essence = _Account_

class Account (_Ancestor_Essence) :
    """An acount which uses passwords for authorization."""

    pw_charset      = \
        ( "abcdefghijklmnopqrstuvwxyz"
          "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
          "0123456789"
        )
    pw_charset_full = "".join ((pw_charset, "$&*+,/:;=?@_"))
    default_ph_name = TFL.Password_Hasher.default.name

    class _Attributes (_Ancestor_Essence._Attributes) :

        class ph_name (A_String) :
            """Name of password hasher used for this account."""

            kind               = Attr.Internal
            Kind_Mixins        = (Attr.Sticky_Mixin, )
            q_able             = False

            def computed_default (self) :
                ### Need to use `self.e_type` to access E_Type
                return self.e_type.default_ph_name
            # end def computed_default

        # end class ph_name

        class password (A_String) :
            """Password for this account"""

            kind               = Attr.Internal
            max_length         = 120
            q_able             = False

        # end class password

    # end class _Attributes

    def change_email_prepare (self, new_email) :
        return self.home_scope.GTW.OMP.Auth.Account_EMail_Verification \
            (self, new_email = new_email).token
    # end def change_email_prepare

    def change_password (self, new_password, remove_actions = True, ** kw) :
        self.set \
            (password = self.password_hash (new_password, self), ** kw)
        if remove_actions :
            Auth = self.home_scope.GTW.OMP.Auth
            for et in ( Auth.Account_Activation
                      , Auth.Account_Password_Change_Required
                      ) :
                for l in et.query (account = self) :
                    l.destroy ()
    # end def change_password

    @classmethod
    def password_hash (cls, password, obj = None) :
        ph_name = obj.ph_name if obj else cls.default_ph_name
        try :
            hasher = TFL.Password_Hasher [ph_name]
        except KeyError :
            cls.unknown_hasher (obj, ph_name)
        else :
            return hasher.hashed (password)
    # end def password_hash

    def prepare_activation (self) :
        password = self.random_password (16)
        self.set \
            ( password  = self.password_hash (password, self)
            , suspended = True
            )
        self.home_scope.GTW.OMP.Auth.Account_Activation (self)
        return password
    # end def prepare_activation

    @classmethod
    def random_password (cls, length = 16) :
        def _gen (cls, length) :
            from   random import choice
            chars = cls.pw_charset_full
            yield choice (cls.pw_charset)
            for i in range (length - 1) :
                yield choice (chars)
        return "".join (_gen (cls, length))
    # end def random_password

    @classmethod
    def unknown_hasher (cls, obj, ph_name) :
        name = obj.name if obj is not None else cls.__name__
        logging.error \
            ( "Unknown password hashing algorithm %r for %r%"
              "\n  Python path\n    %s"
            , ph_name, name, "\n    ".join (sys.path)
            )
        raise KeyError ("No password hasher named '%s'" % ph_name)
    # end def unknown_hasher

    def verify_password (self, password) :
        try :
            hasher = TFL.Password_Hasher [self.ph_name]
        except KeyError :
            self.unknown_hasher (self, self.ph_name)
        else :
            return hasher.verify (password, self.password)
    # end def verify_password

# end class Account

@TFL.Add_To_Class ("Manager", Account)
class Account_Manager (Account.M_E_Type.Manager) :
    """E_Type_Manager specialized for E_Type `Auth.Account`"""

    def apply_migration (self, migration) :
        """Add all objects and links `migration` to `self.home_scope`."""
        scope = self.home_scope
        for k in ("Account", "Group", "Person", "links") :
            for epk, db_attrs in sorted (pyk.iteritems (migration [k])) :
                ET  = scope [epk [-1]]
                obj = ET.instance (* epk, raw = True)
                if obj is None :
                    obj = ET (* epk, raw = True, ** dict (db_attrs))
                elif k == "Account" :
                    obj.set_raw (** dict (db_attrs))
    # end def apply_migration

    def create_new_account_x (self, name, password = None, ** kw) :
        etype = self._etype
        if not password :
            password = etype.random_password (32)
        password = etype.password_hash (password)
        return self \
            ( name
            , password = password
            , ph_name  = etype.default_ph_name
            , ** kw
            )
    # end def create_new_account_x

    def create_new_account (self, name, password) :
        account = self.create_new_account_x \
            (name, password, enabled = True, suspended = True)
        AEV = self.home_scope.GTW.OMP.Auth.Account_EMail_Verification
        return account, AEV (account).token
    # end def create_new_account

    def force_password_change (self, account) :
        Auth = self.home_scope.GTW.OMP.Auth
        if isinstance (account, pyk.string_types) :
            account = self.query (name = account).one ()
        if not Auth.Account_Password_Change_Required.query \
            (account = account).count () :
            Auth.Account_Password_Change_Required (account)
    # end def force_password_change

    def migration (self, * filters) :
        """Return all account instances in migration format."""
        result = dict \
            (  (k, {})
            for k in ("Account", "Group", "Person", "links")
            )
        for obj in self.query (* filters).order_by (Q.pid) :
            result ["Account"].update ((obj.as_migration (), ))
            if getattr (obj, "person", None) :
                result ["Person"].update ((obj.person.as_migration (), ))
                result ["links"].update ((obj.person_link.as_migration (), ))
            for gl in obj.group_links :
                result ["Group"].update ((gl.group.as_migration (), ))
                result ["links"].update ((gl.as_migration (), ))
        return result
    # end def migration

    def reset_password (self, account) :
        Auth  = self.home_scope.GTW.OMP.Auth
        etype = self._etype
        if isinstance (account, pyk.string_types) :
            account = self.query (name = account).one ()
        if not account.enabled :
            raise TypeError ("Account has been disabled")
        ### first we set the password to someting random nobody knows
        account.change_password (etype.random_password (32))
        ### than we create the password change request action
        self.force_password_change (account)
        ### now create a reset password action which contains the new password
        apr = Auth.Account_Password_Reset \
            (account, password = etype.random_password (16))
        ### and temporarily suspend the account
        account.set (suspended = True)
        return apr.password, apr.token
    # end def reset_password

# end class Account_Manager

__doc__ = """

.. autoclass:: _Account_

"""

if __name__ != "__main__" :
    GTW.OMP.Auth._Export ("*")
### __END__ GTW.OMP.Auth.Account
