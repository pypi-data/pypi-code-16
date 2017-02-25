# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.TOP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.TOP.Response
#
# Purpose
#    Extend GTW.RST.Response with session handling
#
# Revision Dates
#    20-Jun-2012 (CT) Creation
#    23-Jul-2012 (CT) Add `username` to `_own_vars`
#     2-May-2013 (CT) Factor `clear_cookie`, `set_cookie`, and
#                     `set_secure_cookie` to `GTW.RST.Response`
#     9-Dec-2013 (CT) Adapt `_set_session_cookie` to signature change of
#                     `set_secure_cookie`
#     9-Dec-2013 (CT) Add `anti_csrf_token`
#    12-Dec-2014 (CT) Consider `session.user.is_valid` in `username.setter`
#    12-Dec-2014 (CT) Increase `max_age` of session cookie to `1<<31`
#    13-Mar-2015 (CT) Change `anti_csrf_token` to method with arg `form_action`
#    17-Mar-2015 (CT) Signify `Anti_CSRF` in `session`
#     9-Jun-2015 (CT) Add guard `self._request.user` to `username`
#    10-Jun-2015 (CT) Add `indicate_notifications`, `notifications_added`
#    10-Jun-2015 (CT) Use `GTW.Notification_Collection` in `add_notification`,
#                     not `_set_session_cookie`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

from   _TFL._Meta.Once_Property import Once_Property

import _GTW._RST._TOP
import _GTW._RST.Response
import _GTW._RST.Signed_Token

import base64
import datetime
import time

class _RST_TOP_Response_ (GTW.RST.Response) :
    """Extend GTW.RST.Response with session handling."""

    _own_vars           = ("notifications_added", "username")

    notifications_added = 0

    @Once_Property
    def session (self) :
        return self._request.session
    # end def session

    @property
    def username (self) :
        if self._request.user :
            ### for anonymous edit sessions there is a random `username` that
            ### doesn't correspond to a user: don't return that!
            return self.session.username
    # end def username

    @username.setter
    def username (self, value) :
        session = self.session
        if value != session.username or not session.user.is_valid :
            session.username = value
            self._set_session_cookie ()
    # end def username

    def add_notification (self, noti) :
        notifications = GTW.Notification_Collection (self.session)
        if notifications is not None :
            if not isinstance (noti, GTW.Notification) :
                noti = GTW.Notification (noti)
            notifications.append (noti)
            self.notifications_added += 1
    # end def add_notification

    def anti_csrf_token (self, form_action = None) :
        request = self._request
        result  = GTW.RST.Signed_Token.Anti_CSRF \
            (request, "don't bug me", form_action = form_action)
        request.session.Anti_CSRF = True
        return result
    # end def anti_csrf_token

    def indicate_notifications (self) :
        added = self.notifications_added
        if added :
            notifications = GTW.Notification_Collection (self.session)
            if len (notifications) :
                ### `notifications` got disgorged
                ### -> this response contains embedded notifications
                ### -> clear the Etag and the last_modified to prevent caching
                self.set_etag ("")
                self.last_modified = datetime.datetime.utcfromtimestamp (0)
    # end def indicate_notifications

    def _set_session_cookie (self) :
        request = self._request
        session = self.session
        name    = request.session_cookie_name
        value   = request.new_secure_cookie (session.sid)
        cookie  = self.set_secure_cookie (name, value, max_age = 1<<31)
        return cookie
    # end def _set_session_cookie

Response = _RST_TOP_Response_ # end class

if __name__ != "__main__" :
    GTW.RST.TOP._Export ("Response")
### __END__ GTW.RST.TOP.Response
