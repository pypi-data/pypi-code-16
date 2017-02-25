# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SMTP
#
# Purpose
#    Support sending of emails via SMTP
#
# Revision Dates
#    19-Feb-2010 (CT) Creation (factored from `PMA.Sender`)
#    21-Feb-2010 (MG) Support for authentication added
#    16-Jun-2010 (CT) s/print/pyk.fprint/
#    27-Dec-2010 (CT) Optional init-arguments added,
#                     `open` and `close` factored and extended (`use_tls`)
#                     `connection` added and used
#    12-Jun-2012 (CT) Import `email.utils`, not `email.Utils` (<= Python 2.4)
#    19-Jun-2012 (CT) Add `header` and apply it in `send_message`
#     6-Jul-2012 (CT) Add `SMTP_Logger`
#    18-Nov-2013 (CT) Change default `charset` to `utf-8`
#    17-Feb-2014 (CT) Change `SMTP_Logger.send` to use `pyk.encoded`
#    31-Mar-2014 (CT) Simplify, and fix, `header` for Python-3
#     8-Oct-2015 (CT) Remove guard against text-type from `__call__`
#                     (Python 3.5 expects `str`, not `bytes`)
#    16-Oct-2015 (CT) Add `__future__` imports
#    20-Oct-2015 (CT) Use `pyk.as_str`
#    20-Oct-2015 (CT) Change `header` to do the same for Python-2 and -3
#    20-Oct-2015 (CT) Add doctests for `SMTP_Logger`, `SMTP_Tester`
#    22-Oct-2015 (CT) Encode `msg` argument to `server.sendmail`
#    23-Oct-2015 (CT) Remove call to `server.close` from `close`
#     4-Nov-2015 (CT) Work around Python-3 bugs
#                     * Use pyk.email_as_bytes
#                     * Use pyk.email_message_from_bytes
#                     * Call `encoders.encode_7or8bit` to ensure a proper
#                       setting of "Content-Transfer-Encoding"
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function

from   _TFL                    import TFL
from   _TFL.pyk                import pyk
from   _TFL.portable_repr      import portable_repr

import _TFL._Meta.Object
import _TFL.Context

from   email                   import encoders, message
from   email.header            import Header, decode_header, make_header
from   email.utils             import formatdate

import datetime
import logging
import smtplib
import sys

class SMTP (TFL.Meta.Object) :
    """Send emails via SMTP"""

    charset        = "utf-8"
    local_hostname = None
    mail_host      = "localhost"
    mail_port      = None
    password       = None
    user           = None
    use_tls        = False

    def __init__ \
            ( self
            , mail_host      = None
            , mail_port      = None
            , local_hostname = None
            , user           = None
            , password       = None
            , use_tls        = None
            , charset        = None
            ) :
        if mail_host is not None :
            self.mail_host = mail_host
        if mail_port is not None :
            self.mail_port = mail_port
        if local_hostname is not None :
            self.local_hostname = local_hostname
        if user is not None :
            self.user = user
        if password is not None :
            self.password = password
        if use_tls is not None :
            self.use_tls = use_tls
        if charset is not None :
            self.charset = charset
        self.server = None
    # end def __init__

    def __call__ (self, text, mail_opts = (), rcpt_opts = None) :
        email = pyk.email_message_from_bytes (pyk.encoded (text, self.charset))
        self.send_message (email, mail_opts = mail_opts, rcpt_opts = rcpt_opts)
    # end def __call__

    def close (self) :
        assert self.server is not None
        try :
            self.server.quit ()
        finally :
            self.server = None
    # end def close

    @TFL.Contextmanager
    def connection (self) :
        close_p = self.server is not None
        server  = self.open ()
        try :
            yield server
        finally :
            if close_p :
                self.close ()
    # end def connection

    def header (self, s, charset = None, ** kw) :
        """Wrap `s` in `email.header.Header` if necessary.

           Wrapping is done only if `s` contains non-ASCII characters;
           applying `Header` to pure ASCII strings adds stupid line noise to
           email addresses!

        >>> smtp = SMTP ()
        >>> print (smtp.header ("christian.tanzer@swing.co.at"))
        christian.tanzer@swing.co.at

        """
        if charset is None :
            charset = self.charset
        result = s
        if isinstance (result, pyk.byte_type) :
            decoded = decode_header (result)
            if any (c for ds, c in decoded) :
                result = make_header \
                    (list ((ds, c or charset) for ds, c in decoded), ** kw)
        if not isinstance (result, Header) :
            if isinstance (result, pyk.byte_type) :
                try :
                    result  = result.decode (charset)
                except UnicodeError :
                    charset = "utf-8"
                    result  = result.decode (charset)
            try :
                result.encode ("ascii")
            except UnicodeError :
                result = Header (s, charset = charset, ** kw)
        return result
    # end def header

    def open (self) :
        if self.server is None :
            result = self.server = smtplib.SMTP \
                (self.mail_host, self.mail_port, self.local_hostname)
            if self.use_tls :
                result.ehlo     ()
                result.starttls () ### Still need another `ehlo` after this
            result.ehlo ()
            if self.user :
                result.login (self.user, self.password)
        return self.server
    # end def open

    def send (self, from_addr, to_addrs, msg, mail_opts = (), rcpt_opts = None) :
        with self.connection () as server :
            msg_x = pyk.encoded (msg, self.charset)
            server.sendmail (from_addr, to_addrs, msg_x, mail_opts, rcpt_opts)
    # end def send

    def send_message (self, email, envelope = None, mail_opts = (), rcpt_opts = None) :
        assert isinstance (email, message.Message)
        if envelope is None :
            envelope = email
        to_addrs = envelope ["To"]
        to       = set (t.strip () for t in to_addrs.split (","))
        for k in "cc", "bcc", "dcc" :
            for h in envelope.get_all (k, []) :
                if h :
                    to.update (t.strip () for t in h.split (","))
            if k != "cc" :
                del email [k]
        if "Date" not in email :
            email ["Date"] = formatdate ()
        if "Content-Type" not in email :
            charset = self.charset
            email ["Content-Type"] = \
                """text/plain; charset="%s" """ % (charset, )
        else :
            charset = email.get_charset ()
        if not email.is_multipart () :
            encoders.encode_7or8bit (email)
        for k in "Subject", "To", "From", "CC", "BCC" :
            vs = email.get_all (k)
            if vs :
                del email [k]
                for v in vs :
                    email [k] = self.header (v, charset, header_name = k)
        ### In Python 3, `email.as_string` is useless because it returns a
        ### base64 encoded body if there are any non-ASCII characters
        ### (setting Content-Transfer-Encoding to "8bit" does *not* help)
        self.send \
            ( envelope ["From"], list (to), pyk.email_as_bytes (email)
            , mail_opts, rcpt_opts
            )
    # end def send_message

# end class SMTP

class SMTP_Logger (SMTP) :
    """Log email using `logging` instead of connecting to SMTP server.

    ::

    >>> smtp = SMTP_Logger (charset = "utf-8")
    >>> smtp (_test_email)

"""

    level = "error"

    def __init__ (self, * args, ** kw) :
        self.pop_to_self      (kw, "level")
        self.__super.__init__ (** kw)
    # end def __init__

    def send (self, from_addr, to_addrs, msg, mail_opts = None, rcpt_opts = None) :
        charset = self.charset
        msg_s   = pyk.decoded (msg, charset)
        self._log \
            ( pyk.as_str ("[%s] Email via %s from %s to %s\n    %s", charset)
            , datetime.datetime.now ().replace (microsecond = 0)
            , pyk.as_str (self.mail_host, charset)
            , pyk.as_str (from_addr, charset)
            , list (pyk.as_str (t, charset) for t in to_addrs)
            , pyk.as_str ("\n    ".join (msg_s.split ("\n")), charset)
            )
    # end def send

    @property
    def _log (self) :
        return getattr (logging, self.level, logging.error)
    # end def _log

# end class SMTP_Logger

class SMTP_Tester (SMTP) :
    """Tester writing to stdout instead of connecting to SMTP server.

       >>> smtp = SMTP_Tester (charset = "utf-8")
       >>> smtp (_test_email)
       Email via localhost from sender@example.com to ['receiver@example.com']
       <BLANKLINE>
       Date: Tue, 20 Oct 2015 14:42:23 -0000
       Content-Type: text/plain; charset="utf-8"
       Content-Transfer-Encoding: 8bit
       Subject: Test email with some diacritics
       To: receiver@example.com
       From: sender@example.com
       <BLANKLINE>
       Test email containing diacritics like ö, ä, ü, and ß.
       <BLANKLINE>

    """

    def send (self, from_addr, to_addrs, msg, mail_opts = None, rcpt_opts = None) :
        pyk.fprint \
            ( "Email via", self.mail_host, "from", from_addr, "to"
            , portable_repr (to_addrs), "\n"
            )
        pyk.fprint (pyk.decoded (msg, self.charset))
    # end def send

# end class SMTP_Tester

_test_email = """\
From: sender@example.com
To: receiver@example.com
Subject: Test email with some diacritics
Date: Tue, 20 Oct 2015 14:42:23 -0000

Test email containing diacritics like ö, ä, ü, and ß.
"""

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.SMTP
