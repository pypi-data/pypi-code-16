# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
# This module is part of the package GTW.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.Notification
#
# Purpose
#    A framework for user notification in a web application
#
# Revision Dates
#    20-Feb-2010 (MG) Creation
#    17-Aug-2012 (MG) Add new `Cached` property and adapt pickle behavior
#    18-Aug-2012 (MG) Fix `discarge` to avoid `empty` head/tail result
#    24-Oct-2014 (CT) Add `Notification_Collection.__repr__`,
#                     use `portable_repr`
#    24-Oct-2014 (CT) Fix spelling: s/discarge/disgorge/g
#    11-Dec-2014 (CT) Add `Notification_Collection.__bool__`
#    16-Dec-2014 (CT) Add missing import for `TFL.Meta.Once_Property`
#    10-Jun-2015 (CT) Add `Notification_Collection.__len__`, `.disgorged`;
#                     remove `Notification_Collection.Cached`
#    10-Jun-2015 (CT) Add `Notification` arg `css_class`, property `datetime`
#    ««revision-date»»···
#--
"""
Short test for the notification framework
    >>> from _GTW.File_Session import File_Session
    >>> time1   = datetime.datetime (2010, 2, 20, 11, 42, 00)
    >>> time2   = datetime.datetime (2010, 2, 20, 11, 42, 42)
    >>> session = File_Session ()
    >>> sid     = session.sid

    >>> nc = Notification_Collection (session)
    >>> nc.append (Notification ("Password reset mail has been sent", time2))
    >>> nc.append (Notification ("User has been logged out",          time1))
    >>> nc
    [Notification ('Password reset mail has been sent', datetime.datetime(2010, 2, 20, 11, 42, 42)), Notification ('User has been logged out', datetime.datetime(2010, 2, 20, 11, 42))]
    >>> session.save                 ()

    >>> session2 = File_Session (sid)
    >>> session != session2
    True
    >>> session2.notifications
    [Notification ('Password reset mail has been sent', datetime.datetime(2010, 2, 20, 11, 42, 42)), Notification ('User has been logged out', datetime.datetime(2010, 2, 20, 11, 42))]
    >>> print (session2.notifications.disgorge ())
    User has been logged out
    Password reset mail has been sent
    >>> print (session2.notifications.disgorge ())
    <BLANKLINE>
    >>> session.remove ()
"""

from   __future__          import print_function

from   _GTW                import GTW
from   _TFL                import TFL

from   _TFL.portable_repr  import portable_repr
from   _TFL.pyk            import pyk

import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL.Accessor

import  datetime

class M_Notification_Collection (TFL.Meta.Object.__class__) :
    """Meta class implementing a singleton pattern"""

    session_key = "notifications"

    def __call__ (cls, session, * args) :
        if cls.session_key not in session :
            session [cls.session_key] = super \
                (M_Notification_Collection, cls).__call__ (* args)
        return session [cls.session_key]
    # end def __call__

# end class M_Notification_Collection

@pyk.adapt__bool__
class Notification_Collection \
          ( TFL.Meta.BaM
              (TFL.Meta.Object, metaclass = M_Notification_Collection)
          ) :
    """Collection of all notifications for a session."""

    def __init__ (self) :
        self._notifications = []
    # end def __init__

    def append (self, arg) :
        self._notifications.append (arg)
    # end def append

    def disgorge (self, head = "", joiner = "\n", tail = "") :
        items  = tuple (self._notifications)
        result = []
        if items :
            result.append (head)
            result.append \
                ( joiner.join
                    (  pyk.text_type (s)
                    for s in sorted (items, key = TFL.Getter.time)
                    )
                )
            result.append (tail)
            self._notifications = []
        return "".join (result)
    # end def disgorge

    def disgorged (self) :
        result, self._notifications = self._notifications, []
        return sorted (result, key = TFL.Getter.time)
    # end def disgorged

    def __bool__ (self) :
        return bool (self._notifications)
    # end def __bool__

    def __getstate__ (self) :
        return self.__dict__
    # end def __getstate__

    def __iter__ (self) :
        return iter (self._notifications)
    # end def __iter__

    def __len__ (self) :
        return len (self._notifications)
    # end def __len__

    def __repr__ (self) :
        return portable_repr (self._notifications)
    # end def __repr__

# end class Notification_Collection

@pyk.adapt__str__
class Notification (TFL.Meta.Object) :
    """A notification based on plain text."""

    def __init__ (self, message, time = None, css_class = None) :
        self.message   = message
        self.time      = time or datetime.datetime.now ()
        self.css_class = css_class
    # end def __init__

    @TFL.Meta.Once_Property
    def datetime (self) :
        dt = self.time
        if isinstance (dt, datetime.datetime) :
            return dt.strftime ("%Y-%m-%d %H:%M:%S")
    # end def datetime

    def __repr__ (self) :
        return pyk.reprify \
            ( "%s (%s, %s)"
            % ( self.__class__.__name__
              , portable_repr (self.message)
              , portable_repr (self.time)
              )
            )
    # end def __repr__

    def __str__ (self) :
        return self.message
    # end def __str__

# end class Notification

if __name__ != "__main__" :
    GTW._Export ("*")
### __END__ GTW.Notification
