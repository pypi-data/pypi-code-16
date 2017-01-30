"""
    Slixmpp: The Slick XMPP Library
    Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
    This file is part of Slixmpp.

    See the file LICENSE for copying permission.
"""

import datetime as dt

from slixmpp.jid import JID
from slixmpp.xmlstream import ElementBase
from slixmpp.plugins import xep_0082


class LegacyDelay(ElementBase):

    name = 'x'
    namespace = 'jabber:x:delay'
    plugin_attrib = 'legacy_delay'
    interfaces = {'from', 'stamp', 'text'}

    def get_from(self):
        from_ = self._get_attr('from')
        return JID(from_) if from_ else None

    def set_from(self, value):
        self._set_attr('from', str(value))

    def get_stamp(self):
        timestamp = self._get_attr('stamp')
        return xep_0082.parse('%sZ' % timestamp) if timestamp else None

    def set_stamp(self, value):
        if isinstance(value, dt.datetime):
            value = value.astimezone(xep_0082.tzutc)
            value = xep_0082.format_datetime(value)
        self._set_attr('stamp', value[0:19].replace('-', ''))

    def get_text(self):
        return self.xml.text

    def set_text(self, value):
        self.xml.text = value

    def del_text(self):
        self.xml.text = ''
