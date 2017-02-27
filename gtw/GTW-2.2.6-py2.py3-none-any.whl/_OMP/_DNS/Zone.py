# -*- coding: utf-8 -*-
# Copyright (C) 2012 Dr. Ralf Schlatterbeck All rights reserved
# Reichergasse 131, A-3411 Weidling, Austria. rsc@runtux.com
# #*** <License> ************************************************************#
# This package is part of the package GTW.OMP.DNS.
# 
# This package is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    DNS.Zone
#
# Purpose
#    Model a DNS Zone
#
# Revision Dates
#    27-Aug-2012 (RS) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _MOM.import_MOM          import *
from   _GTW._OMP._DNS           import DNS
import _GTW._OMP._DNS.Entity
from   _GTW._OMP._DNS.Attr_Type import *

_Ancestor_Essence = DNS.Object

class Zone (_Ancestor_Essence) :
    """A DNS Zone"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class name (A_DNS_Name) :
            """Name of the zone"""

            kind               = Attr.Primary

        # end class name

        class refresh (A_DNS_Time) :
            """Refresh time for secondary DNS servers"""

            kind               = Attr.Necessary
            desc               = \
                ( u"Time after which the zone should be refreshed by a"
                   " secondary DNS server."
                   " How often a secondary will poll the primary server"
                   " to see if the serial number for the zone has"
                   " increased (so it knows to request a new copy of the"
                   " data for the zone).  Set this to how long your"
                   " secondaries can comfortably contain out-of-date data."
                   " You can keep it short (20 mins to 2 hours) if you"
                   " aren't worried about a small increase in bandwidth"
                   " used, or longer (2-12 hours) if your Internet"
                   " connection is slow or is started on demand.  Recent"
                   " BIND versions (4.9.3) have optional code to"
                   " automatically notify secondaries that data has"
                   " changed, allowing you to set this TTL to a long value"
                   " (one day, or more). [from RFC 1912]"
                )

        # end class refresh

        class retry (A_DNS_Time) :
            """Retry time for secondary DNS servers"""

            kind               = Attr.Necessary
            desc               = \
                ( u"If a secondary was unable to contact the primary at"
                   " the last refresh, wait the retry value before"
                   " trying again.  This value isn't as important as"
                   " others, unless the secondary is on a distant network"
                   " from the primary or the primary is more prone to"
                   " outages.  It's typically some fraction of the refresh"
                   " interval. [from RFC 1912]"
                )

        # end class retry

        class expire (A_DNS_Time) :
            """Expire time on secondary DNS servers"""

            kind               = Attr.Necessary
            desc               = \
                ( u"How long a secondary will still treat its copy of"
                   " the zone data as valid if it can't contact the"
                   " primary.  This value should be greater than how"
                   " long a major outage would typically last, and must"
                   " be greater than the minimum and retry intervals, to"
                   " avoid having a secondary expire the data before it"
                   " gets a chance to get a new copy.  After a zone is"
                   " expired a secondary will still continue to try to"
                   " contact the primary, but it will no longer provide"
                   " nameservice for the zone.  2-4 weeks are suggested"
                   " values. [from RFC 1912]"
                )

        # end class expire

        class minimum (A_DNS_Time) :
            """Time to live of negative responses."""

            kind               = Attr.Necessary
            max_value          = 60 * 60 * 24
            desc               = \
                ( u"Time to live (TTL) of negative responses used by all"
                   " caching DNS servers. The minimum of this field and"
                   " the SOA's time to live field is used for the time of"
                   " caching negative (NXDOMAIN or NODATA) DNS answers."
                   " In the past this field has been used as the default"
                   " TTL for records not specifying an explicit TTL."
                   " RFC 2308 deprecates this use and specifies an"
                   " explicit $TTL field in the DNS master file format.\n"
                   'RFC 2308: "The SOA minimum field has been overloaded'
                   " in the past to have three different meanings, the"
                   " minimum TTL value of all RRs in a zone, the default"
                   " TTL of RRs which did not contain a TTL value and"
                   " the TTL of negative responses.\n"
                   "Despite being the original defined meaning, the"
                   " first of these, the minimum TTL value of all RRs in a"
                   " zone, has never in practice been used and is hereby"
                   " deprecated.\n"
                   "The second, the default TTL of RRs which contain no"
                   " explicit TTL in the master zone file, is relevant"
                   " only at the primary server.  After a zone transfer"
                   " all RRs have explicit TTLs and it is impossible to"
                   " determine whether the TTL for a record was explicitly"
                   " set or derived from the default after a zone"
                   " transfer. Where a server does not require RRs to"
                   " include the TTL value explicitly, it should provide a"
                   " mechanism, not being the value of the MINIMUM field"
                   " of the SOA record, from which the missing TTL values"
                   " are obtained.  How this is done is implementation"
                   " dependent. [...] Values of one to three hours have"
                   " been found to work well and would make sensible a"
                   " default.  Values exceeding one day have been found"
                   ' to be problematic."'
                )

        # end class minimum

        class ttl (A_DNS_Time) :
            """Time to live"""

            kind               = Attr.Necessary
            desc               = \
                ( u"Default time to live for records not"
                   " specifying a TTL value. For a description of the"
                   " arithmetics involved, see RFC 1982."
                )

        # end class ttl

    # end class _Attributes

# end class Zone

if __name__ != "__main__" :
    DNS._Export ("*")
### __END__ DNS.Zone
