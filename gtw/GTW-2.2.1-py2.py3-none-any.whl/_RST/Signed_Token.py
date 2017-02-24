# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.Signed_Token
#
# Purpose
#    Signed token as used for secure cookies or CSRF tokens
#
# Revision Dates
#     6-Dec-2013 (CT) Creation
#    11-Dec-2013 (CT) Use `request.host`, not `.host_url`, for `Anti_CSRF`
#    24-Feb-2014 (CT) Change `__repr__` to use `pyk.encoded`
#    12-Oct-2014 (CT) Use `TFL.Secure_Hash`
#    12-Dec-2014 (CT) Add `request.path` to `Anti_CSRF.secrets`
#    13-Mar-2015 (CT) Add `form_action` to `Anti_CSRF`
#    10-Jun-2015 (CT) Adapt doctest to `form_action`, `request.path`
#                     in `Anti_CSRF`
#     7-Oct-2015 (CT) Add more `pyk.encoded`, `pyk.decoded` calls (Python 3.5)
#    21-Oct-2015 (CT) Define `sig_sep` as `str`, not `bytes`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.portable_repr       import portable_repr
from   _TFL.pyk                 import pyk

import _GTW._RST

import _TFL._Meta.Object

import base64
import datetime
import logging
import time

@pyk.adapt__bool__
@pyk.adapt__str__
class _Base_ (TFL.Meta.Object) :
    """Signed token as used for secure cookies or CSRF tokens"""

    cargo                      = ""
    data                       = None
    encoding                   = "utf-8"
    secret_x                   = None
    sig_sep                    = ":::"
    timestamp                  = ""
    val_sep                    = "|"
    x_signature                = ""
    x_value                    = ""

    _invalid                   = False
    _value                     = None

    def __init__ (self, request, data, ** kw) :
        time  = request.current_time
        b64ed = lambda x : \
            pyk.decoded (base64.b64encode (pyk.encoded (x, self.encoding)))
        self.__dict__.update \
            ( cargo     = b64ed (data)
            , data      = data
            , request   = request
            , time      = time
            , timestamp = b64ed (int (time))
            , ** kw
            )
    # end def __init__

    @classmethod
    def recover (cls, request, value, ttl_s = None) :
        """Recover a signed token from `value`"""
        root   = request.root
        result = cls.__new__ (cls)
        result.request = request
        result.x_value = value
        parts  = value.split (cls.val_sep, 2)
        if len (parts) != 3 :
            if value :
                fmt = _ ("Malformed %s value '%s'")
            else :
                fmt = _ ("Missing %s%s")
            result._invalid = _T (fmt) % (cls.__name__, value)
            return result
        (result.cargo, result.timestamp, result.x_signature) = parts
        enc = result.encoding
        try:
            result.data = data = base64.b64decode (result.cargo).decode (enc)
        except Exception as exc :
            result._invalid = str (exc)
            return result
        if not root.HTTP.safe_str_cmp (result.x_signature, result.signature) :
            result._invalid = msg = \
                _T ("Invalid %s signature for '%s'") % (cls.__name__, data)
            logging.warning (msg)
        try :
            timestamp = base64.b64decode (result.timestamp).decode (enc)
        except Exception as exc :
            result._invalid = repr (exc)
        else :
            try :
                then = result.time = int (timestamp)
            except Exception as exc :
                result._invalid = repr (exc)
        if result :
            now = request.current_time
            ttl = ttl_s if ttl_s is not None else request.resource.session_ttl_s
            if then < (now - ttl) :
                result._invalid = msg = \
                    ( _T ("Expired %s '%s' older then %s seconds")
                    % (cls.__name__, data, ttl)
                    )
                logging.warning (msg)
            elif then > now + 180 :
                ### don't accept tokens with a timestamp more than 2 minutes in
                ### the future
                result._invalid = msg = \
                    ( _T ("Time-travelling %s '%s' [%s seconds ahead]")
                    % (cls.__name__, data, then - now)
                    )
                logging.warning (msg)
        return result
    # end def recover

    @Once_Property
    def secrets (self) :
        result   = (self.request.cookie_salt, )
        secret_x = self.secret_x
        return result + ((secret_x, ) if secret_x else ())
    # end def secrets

    @Once_Property
    def signature (self) :
        return self._signature (self.request, self.secrets, * self.sig_parts)
    # end def signature

    @Once_Property
    def sig_parts (self) :
        return (self.cargo, self.timestamp)
    # end def sig_parts

    @Once_Property
    def value (self) :
        result = self._value
        if result is None :
            sig    = pyk.decoded (self.signature, self.encoding)
            result = self._value = self.val_sep.join \
                ((self.cargo, self.timestamp, sig))
        return result
    # end def value

    def _signature (self, request, secrets, * parts) :
        result  = request.root.hash_fct.hmac (secrets)
        sig_sep = self.sig_sep
        for p in parts :
            result.update (sig_sep)
            result.update (p)
        return result.hexdigest ()
    # end def _signature

    def __bool__ (self) :
        return not any ((self.data is None, self._invalid))
    # end def __bool__

    def __eq__ (self, rhs) :
        return self.value == getattr (rhs, "value", object ())
    # end def __eq__

    def __hash__ (self) :
        return hash (self.value)
    # end def __hash__

    def __repr__ (self) :
        result = "%s: %s, %s" % \
            ( self.__class__.__name__
            , portable_repr (self.data)
            , portable_repr (self.secrets)
            )
        if self._invalid :
            result = "%s\n    %s" % (result, self._invalid)
        return pyk.reprify (result)
    # end def __repr__

    def __str__ (self) :
        return pyk.decoded (self.value)
    # end def __str__

# end class _Base_

class Cookie (_Base_) :
    """Cookie token"""

    @Once_Property
    def secrets (self) :
        request = self.request
        result  = self.__super.secrets + (request.host_url, )
        return result
    # end def secrets

# end class Cookie

class Anti_CSRF (_Base_) :
    """CSRF prevention token"""

    form_action = None

    @Once_Property
    def secrets (self) :
        request     = self.request
        form_action = self.form_action
        result      = self.__super.secrets + \
            ( request.session.sid
            , request.host
            , form_action or request.path
            )
        return result
    # end def secrets

# end class Anti_CSRF

class REST_Auth (_Base_) :
    """REST authentication token"""

    _account   = None

    @property
    def account (self) :
        result = self._account
        if result is None :
            data = self.data
            root = self.request.root
            try :
                pid = int (data)
            except Exception :
                result = root._get_user (data)
            else :
                result = root.scope.pid_query (pid)
            self._account = result
        return result
    # end def account

    @account.setter
    def account (self, value) :
        self._account = value
    # end def account

    @Once_Property
    def secrets (self) :
        request = self.request
        rip     = getattr (request, "remote_addr", None)
        scope   = request.root.scope
        account = self.account
        if account is not None :
            return self.__super.secrets + \
                (account.password, scope.db_meta_data.dbid, account.pid, rip)
    # end def secrets

# end class REST_Auth

__doc__ = r"""

    >>> from   _GTW._Werkzeug import Werkzeug
    >>> from   _TFL.Record    import Record
    >>> import _GTW._Werkzeug.Request
    >>> import _TFL.Secure_Hash

    >>> req = Record \
    ...     ( cookie_salt  = "<some-salt>"
    ...     , current_time = 1234.56789
    ...     , host         = "localhost"
    ...     , host_url     = "http://localhost/"
    ...     , path         = None
    ...     , remote_addr  = "111.222.333.444"
    ...     , root         = Record
    ...         ( HTTP     = Werkzeug
    ...         , hash_fct = TFL.Secure_Hash.sha224
    ...         , scope    = Record (db_meta_data = Record (dbid = "ABCDEFG"))
    ...         )
    ...     , session      = Record (sid = 4711)
    ...     )
    >>> req_f = req.copy (current_time = req.current_time + 7200)
    >>> req_p = req.copy (current_time = req.current_time - 7200)
    >>> req_s = req.copy (cookie_salt  = "<some-other-salt>")
    >>> REST_Auth._account = Record \
    ...     ( password     = "notsecret"
    ...     , pid          = 42
    ...     )

    >>> cookie = Cookie (req, "<session-id-value>")
    >>> print (cookie.value)
    PHNlc3Npb24taWQtdmFsdWU+|MTIzNA==|4340000bee991260b760b1e6460dcea2774d30fa66cca990ab3c9e07

    >>> cr = Cookie.recover (req, cookie.value, ttl_s = 3600)
    >>> cr
    Cookie: '<session-id-value>', ('<some-salt>', 'http://localhost/')
    >>> print (cr.value)
    PHNlc3Npb24taWQtdmFsdWU+|MTIzNA==|4340000bee991260b760b1e6460dcea2774d30fa66cca990ab3c9e07

    >>> cookie == cr
    True

    >>> cf = Cookie.recover (req_f, cookie.value, ttl_s = 3600)
    >>> cf
    Cookie: '<session-id-value>', ('<some-salt>', 'http://localhost/')
        Expired Cookie '<session-id-value>' older then 3600 seconds
    >>> bool (cf)
    False

    >>> cp = Cookie.recover (req_p, cookie.value, ttl_s = 3600)
    >>> cp
    Cookie: '<session-id-value>', ('<some-salt>', 'http://localhost/')
        Time-travelling Cookie '<session-id-value>' [7199.43211 seconds ahead]
    >>> bool (cp)
    False

    >>> cs = Cookie.recover (req_s, cookie.value, ttl_s = 3600)
    >>> cs
    Cookie: '<session-id-value>', ('<some-other-salt>', 'http://localhost/')
        Invalid Cookie signature for '<session-id-value>'
    >>> bool (cs)
    False

    >>> act = Anti_CSRF (req, "<form-id?>")
    >>> print (act.value)
    PGZvcm0taWQ/Pg==|MTIzNA==|801bcb45abeae2881e0c0b47031739128692ce4358602ba736b70f50

    >>> ar = Anti_CSRF.recover (req, act.value, ttl_s = 3600)
    >>> ar
    Anti_CSRF: '<form-id?>', ('<some-salt>', 4711, 'localhost', None)

    >>> act == ar
    True

    >>> rat = REST_Auth (req, "<user-x>")
    >>> print (rat.value)
    PHVzZXIteD4=|MTIzNA==|908a81969010fb575ef4305b8a1e2d267e6470a145404f6187e73ea4

    >>> rr = REST_Auth.recover (req, rat.value, ttl_s = 3600)
    >>> rr
    REST_Auth: '<user-x>', ('<some-salt>', 'notsecret', 'ABCDEFG', 42, '111.222.333.444')

    >>> rat == rr
    True

    >>> REST_Auth.recover (req, "made-up token value")
    REST_Auth: None, ('<some-salt>', 'notsecret', 'ABCDEFG', 42, '111.222.333.444')
        Malformed REST_Auth value 'made-up token value'

"""

if __name__ != "__main__" :
    GTW.RST._Export_Module ()
### __END__ GTW.RST.Signed_Token
