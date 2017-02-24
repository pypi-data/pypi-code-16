# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Dr. Ralf Schlatterbeck All rights reserved
# Reichergasse 131, A--3411 Weidling, Austria. rsc@runtux.com
# #*** <License> ************************************************************#
# This module is part of the package GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.__test__.Attr_Net
#
# Purpose
#    Test cases for GTW.OMP.Net.Attr_Type
#
# Revision Dates
#    22-May-2012 (RS) Creation
#    10-Aug-2012 (RS) IP addresses are now composite. Fix tests for new
#                     check of subnet mask (bits right of mask must be 0)
#    11-Aug-2012 (MG) New tests for query functions added
#    13-Aug-2012 (RS) Test `IP6_Network` with default mask_len 128
#    13-Sep-2012 (RS) Comment doctest for unimplemented feature
#    24-Sep-2012 (RS) Fix doctest for `in`, add relational operators
#                     fix error messages now coming from rsclib
#    24-Sep-2012 (CT) Adapt tests
#    10-Oct-2012 (CT) Rename test classes to `Test_...`
#    10-Oct-2012 (CT) Add test for `raw_query_attrs`
#    11-Oct-2012 (RS) Add type-check for `raw_query_attrs` test
#    12-Oct-2012 (CT) Adapt to repr change of `An_Entity`
#    12-Oct-2012 (RS) Changed `code_format` in `GTW.OMP.NET.Attr_Type`
#     7-Mar-2013 (RS) Test `CONTAINS`
#     6-Aug-2013 (CT) Adapt to major surgery of GTW.OMP.NET.Attr_Type
#    18-Aug-2013 (RS) Fix sort order of IP networks
#    29-Apr-2014 (RS) Fix traceback messages for new rsclib
#    ««revision-date»»···
#--

from   __future__               import print_function, unicode_literals

from   _MOM.import_MOM          import *
from   _GTW._OMP._NET.Attr_Type import *
from   _TFL.Package_Namespace   import Derived_Package_Namespace

Namespace = Derived_Package_Namespace (parent = MOM, name = "_GTW._OMP._NET")

_Ancestor_Essence = MOM.Object

class Test_IP4_Address (_Ancestor_Essence) :

    PNS = Namespace

    class _Attributes (_Ancestor_Essence._Attributes) :

        class address (A_IP4_Address) :

            kind = Attr.Primary

        # end class address

    # end class _Attributes

# end class Test_IP4_Address

_Ancestor_Essence = MOM.Object

class Test_IP4_Network (_Ancestor_Essence) :

    PNS = Namespace

    class _Attributes (_Ancestor_Essence._Attributes) :

        class address (A_IP4_Network) :

            kind = Attr.Primary

        # end class address

    # end class _Attributes

# end class Test_IP4_Network

_Ancestor_Essence = MOM.Object

class Test_IP6_Address (_Ancestor_Essence) :

    PNS = Namespace

    class _Attributes (_Ancestor_Essence._Attributes) :

        class address (A_IP6_Address) :

            kind = Attr.Primary

        # end class address

    # end class _Attributes

# end class Test_IP6_Address

_Ancestor_Essence = MOM.Object

class Test_IP6_Network (_Ancestor_Essence) :

    PNS = Namespace

    class _Attributes (_Ancestor_Essence._Attributes) :

        class address (A_IP6_Network) :

            kind = Attr.Primary

        # end class address

    # end class _Attributes

# end class Test_IP6_Network

_Ancestor_Essence = MOM.Object

class MAC_Address (_Ancestor_Essence) :

    PNS = Namespace

    class _Attributes (_Ancestor_Essence._Attributes) :

        class address (A_MAC_Address) :

            kind = Attr.Primary

        # end class address

    # end class _Attributes

# end class MAC_Address

_test_ip4 = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> NET = scope.GTW.OMP.NET
    >>> Test_IP4_Address = NET.Test_IP4_Address
    >>> Test_IP4_Network = NET.Test_IP4_Network

    >>> Test_IP4_Address ('1.2.3.4', raw = True)
    GTW.OMP.NET.Test_IP4_Address ("1.2.3.4")

    >>> Test_IP4_Address (address = '111.222.233.244', raw = True)
    GTW.OMP.NET.Test_IP4_Address ("111.222.233.244")

    >>> Test_IP4_Address ('111.222.233.244/22', raw = True)
    Traceback (most recent call last):
     ...
    Attribute_Value: Can't set IP4-address `address` attribute Test_IP4_Address.address to 111.222.232.0/22.
        Invalid netmask: 22; must be empty or 32

    >>> Test_IP4_Address (address = '1.2.3.4/22', raw = True)
    Traceback (most recent call last):
     ...
    Attribute_Value: Can't set IP4-address `address` attribute Test_IP4_Address.address to 1.2.0.0/22.
        Invalid netmask: 22; must be empty or 32

    >>> Test_IP4_Address (address = '256.255.255.2', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP4_Address: Syntax: Invalid octet: 256` for : `IP4-address `address``
         expected type  : 'IP4-address'
         got      value : '256.255.255.2'
    IP4 address must contain 4 decimal octets separated by `.`.
    >>> Test_IP4_Address (address = '2560.255.2.2', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP4_Address: Syntax: Invalid octet: 2560` for : `IP4-address `address``
         expected type  : 'IP4-address'
         got      value : '2560.255.2.2'
    IP4 address must contain 4 decimal octets separated by `.`.
    >>> Test_IP4_Network (address = '111.222.233.244/31', raw = True)
    GTW.OMP.NET.Test_IP4_Network ("111.222.233.244/31")
    >>> Test_IP4_Network (address = '1.2.3.4/30', raw = True)
    GTW.OMP.NET.Test_IP4_Network ("1.2.3.4/30")
    >>> Test_IP4_Network (address = '1.2.3.4/32', raw = True)
    GTW.OMP.NET.Test_IP4_Network ("1.2.3.4")
    >>> Test_IP4_Network (address = '0.0.0.0/0', raw = True)
    GTW.OMP.NET.Test_IP4_Network ("0.0.0.0/0")
    >>> Test_IP4_Network (address = '1.2.3.4/22', raw = True)
    GTW.OMP.NET.Test_IP4_Network ("1.2.0.0/22")
    >>> Test_IP4_Network (address = '1.2.3.4/33', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP4_Address: Syntax: Invalid netmask: 33` for : `IP4-network `address``
         expected type  : 'IP4-network'
         got      value : '1.2.3.4/33'
    IP4 network must contain 4 decimal octets separated by `.`, optionally followed by `/` and a number between 0 and 32. The bits right of the netmask are automatically set to zero.
    >>> Test_IP4_Network (address = '1.2.3.4/333', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP4_Address: Syntax: Invalid netmask: 333` for : `IP4-network `address``
         expected type  : 'IP4-network'
         got      value : '1.2.3.4/333'
    IP4 network must contain 4 decimal octets separated by `.`, optionally followed by `/` and a number between 0 and 32. The bits right of the netmask are automatically set to zero.

"""

_test_ip6 = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> NET = scope.GTW.OMP.NET
    >>> Test_IP6_Address = NET.Test_IP6_Address
    >>> Test_IP6_Network = NET.Test_IP6_Network

    >>> Test_IP6_Address \\
    ...     ( address = '2001:0db8:85a3:0000:0000:8a2e:0370:7334'
    ...     , raw = True
    ...     )
    GTW.OMP.NET.Test_IP6_Address ("2001:db8:85a3::8a2e:370:7334")
    >>> Test_IP6_Address \\
    ...     ( address = '2001:db8:85a3:0:0:8a2e:370:7335'
    ...     , raw = True
    ...     )
    GTW.OMP.NET.Test_IP6_Address ("2001:db8:85a3::8a2e:370:7335")
    >>> Test_IP6_Address \\
    ...     ( address = '2001:db8:85a3::8a2e:370:7336'
    ...     , raw = True
    ...     )
    GTW.OMP.NET.Test_IP6_Address ("2001:db8:85a3::8a2e:370:7336")
    >>> Test_IP6_Address \\
    ...     ( address = '2001:0db8:0000:0000:0000:0000:1428:57ab'
    ...     , raw = True
    ...     )
    GTW.OMP.NET.Test_IP6_Address ("2001:db8::1428:57ab")
    >>> Test_IP6_Address \\
    ...     ( address = '2001:0db8:0000:0000:0000::1428:57ac'
    ...     , raw = True
    ...     )
    GTW.OMP.NET.Test_IP6_Address ("2001:db8::1428:57ac")
    >>> Test_IP6_Address (address = '2001:0db8:0:0:0:0:1428:57ad', raw = True)
    GTW.OMP.NET.Test_IP6_Address ("2001:db8::1428:57ad")
    >>> Test_IP6_Address (address = '2001:0db8:0:0::1428:57ae', raw = True)
    GTW.OMP.NET.Test_IP6_Address ("2001:db8::1428:57ae")
    >>> Test_IP6_Address (address = '2001:0db8::1428:57af', raw = True)
    GTW.OMP.NET.Test_IP6_Address ("2001:db8::1428:57af")
    >>> Test_IP6_Address (address = '2001:db8::1428:57b0', raw = True)
    GTW.OMP.NET.Test_IP6_Address ("2001:db8::1428:57b0")
    >>> Test_IP6_Address \\
    ...     ( address = '0000:0000:0000:0000:0000:0000:0000:0001'
    ...     , raw = True
    ...     )
    GTW.OMP.NET.Test_IP6_Address ("::1")
    >>> Test_IP6_Address (address = '::2', raw = True)
    GTW.OMP.NET.Test_IP6_Address ("::2")
    >>> Test_IP6_Address (address = '::ffff:0c22:384e', raw = True)
    GTW.OMP.NET.Test_IP6_Address ("::ffff:c22:384e")
    >>> Test_IP6_Address \\
    ...     ( address = '2001:0db8:1234:0000:0000:0000:0000:0000'
    ...     , raw = True
    ...     )
    GTW.OMP.NET.Test_IP6_Address ("2001:db8:1234::")
    >>> Test_IP6_Address \\
    ...     ( address = '2001:0db8:1234:ffff:ffff:ffff:ffff:ffff'
    ...     , raw = True
    ...     )
    GTW.OMP.NET.Test_IP6_Address ("2001:db8:1234:ffff:ffff:ffff:ffff:ffff")
    >>> Test_IP6_Address (address = '2001:db8:a::123', raw = True)
    GTW.OMP.NET.Test_IP6_Address ("2001:db8:a::123")
    >>> Test_IP6_Address (address = 'fe80::', raw = True)
    GTW.OMP.NET.Test_IP6_Address ("fe80::")
    >>> Test_IP6_Address (address = '::ffff:c000:280', raw = True)
    GTW.OMP.NET.Test_IP6_Address ("::ffff:c000:280")
    >>> Test_IP6_Address (address = '::', raw = True)
    GTW.OMP.NET.Test_IP6_Address ("::")
    >>> Test_IP6_Address (address = '::ffff:12.34.56.78', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Hex value too long: 12.34.56.78` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : '::ffff:12.34.56.78'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = '::ffff:192.0.2.128', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Hex value too long: 192.0.2.128` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : '::ffff:192.0.2.128'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = '123', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Not enough hex parts in 123` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : '123'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = 'ldkfj', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Hex value too long: ldkfj` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : 'ldkfj'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = '2001::FFD3::57ab', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Only one '::' allowed` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : '2001::FFD3::57ab'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address \\
    ...     ( address = '2001:db8:85a3::8a2e:37023:7334'
    ...     , raw = True
    ...     )
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Hex value too long: 37023` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : '2001:db8:85a3::8a2e:37023:7334'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address \\
    ...     ( address = '2001:db8:85a3::8a2e:370k:7334'
    ...     , raw = True
    ...     )
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: invalid literal for long() with base 16: '370k'` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : '2001:db8:85a3::8a2e:370k:7334'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = '1:2:3:4:5:6:7:8:9', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Too many hex parts in 1:2:3:4:5:6:7:8:9` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : '1:2:3:4:5:6:7:8:9'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = '1::2::3', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Only one '::' allowed` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : '1::2::3'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = '1:::3:4:5', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Too many ':': 1:::3:4:5` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : '1:::3:4:5'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = '1:2:3::4:5:6:7:8:9', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Too many hex parts in 1:2:3::4:5:6:7:8:9` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : '1:2:3::4:5:6:7:8:9'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = '::ffff:2.3.4', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Hex value too long: 2.3.4` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : '::ffff:2.3.4'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = '::ffff:257.1.2.3', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Hex value too long: 257.1.2.3` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : '::ffff:257.1.2.3'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = '1.2.3.4', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Hex value too long: 1.2.3.4` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : '1.2.3.4'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = ':aa:aa:aa', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: No single ':' at start allowed` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : ':aa:aa:aa'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = 'aa:aa:aa:', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: No single ':' at end allowed` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : 'aa:aa:aa:'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = '1:2:3:4:5:6:7', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Not enough hex parts in 1:2:3:4:5:6:7` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : '1:2:3:4:5:6:7'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = ':::', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: No ':' at start and end` for : `IP6-address `address``
         expected type  : 'IP6-address'
         got      value : ':::'
    IP6 address must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used.
    >>> Test_IP6_Address (address = '1:2:3::/127', raw = True)
    Traceback (most recent call last):
     ...
    Attribute_Value: Can't set IP6-address `address` attribute Test_IP6_Address.address to 1:2:3::/127.
        Invalid netmask: 127; must be empty or 128

    >>> Test_IP6_Network (address = '1:2:3::/48', raw = True)
    GTW.OMP.NET.Test_IP6_Network ("1:2:3::/48")
    >>> Test_IP6_Network (address = '1:2:3::/128', raw = True)
    GTW.OMP.NET.Test_IP6_Network ("1:2:3::")

    >>> n = Test_IP6_Network (address = '2001:db8:a::123', raw = True)
    >>> n
    GTW.OMP.NET.Test_IP6_Network ("2001:db8:a::123")

    >>> n.address, n.address.__class__.__name__
    (2001:db8:a::123, 'IP6_Address')

    >>> int (n.address.mask)
    128

    >>> Test_IP6_Network (address = '::/0', raw = True)
    GTW.OMP.NET.Test_IP6_Network ("::/0")
    >>> Test_IP6_Network (address = '1:2:3::/1', raw = True)
    GTW.OMP.NET.Test_IP6_Network ("::/1")
    >>> Test_IP6_Network (address = '1:2:3::/129', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Invalid netmask: 129` for : `IP6-network `address``
         expected type  : 'IP6-network'
         got      value : '1:2:3::/129'
    IP6 network must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used. This is optionally followed by `/` and a number between 0 and 128. The bits right of the netmask are automatically set to zero.
    >>> Test_IP6_Network (address = '1:2:3::/1290', raw = True)
    Traceback (most recent call last):
     ...
    Invariants: `IP6_Address: Syntax: Invalid netmask: 1290` for : `IP6-network `address``
         expected type  : 'IP6-network'
         got      value : '1:2:3::/1290'
    IP6 network must contain up to 8 hexadecimal numbers with up to 4 digits separated by `:`. A single empty group `::` can be used. This is optionally followed by `/` and a number between 0 and 128. The bits right of the netmask are automatically set to zero.

"""

_test_mac = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> NET = scope.GTW.OMP.NET
    >>> MAC_Address = NET.MAC_Address

    >>> MAC_Address ("00:11:22:33:44:55")
    GTW.OMP.NET.MAC_Address ('00:11:22:33:44:55')

    >>> MAC_Address ("000:11:22:33:44:55")
    Traceback (most recent call last):
     ...
    Invariants: Condition `AC_check_address_length` : Value for address must not be longer than 17 characters (length <= 17)
        address = '000:11:22:33:44:55'
        length = 18 << len (address)
      `Syntax error` for : `MAC-address `address``
         expected type  : 'MAC-address'
         got      value : '000:11:22:33:44:55'
    A MAC address must contain 6 hexadecimal octets separated by `:`.

    >>> MAC_Address ("00:11:22:33:44")
    Traceback (most recent call last):
     ...
    Invariants: `Syntax error` for : `MAC-address `address``
         expected type  : 'MAC-address'
         got      value : '00:11:22:33:44'
    A MAC address must contain 6 hexadecimal octets separated by `:`.

    >>> MAC_Address ("00:11:22:33:44:55:66")
    Traceback (most recent call last):
     ...
    Invariants: Condition `AC_check_address_length` : Value for address must not be longer than 17 characters (length <= 17)
        address = '00:11:22:33:44:55:66'
        length = 20 << len (address)
      `Syntax error` for : `MAC-address `address``
         expected type  : 'MAC-address'
         got      value : '00:11:22:33:44:55:66'
    A MAC address must contain 6 hexadecimal octets separated by `:`.

"""

_test_query = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> NET = scope.GTW.OMP.NET
    >>> Test_IP4_Address = NET.Test_IP4_Address
    >>> Test_IP4_Network = NET.Test_IP4_Network
    >>> Test_IP6_Address = NET.Test_IP6_Address
    >>> Test_IP6_Network = NET.Test_IP6_Network

    >>> i40 = Test_IP4_Address (address = '192.168.0.1',    raw = True)
    >>> i41 = Test_IP4_Address (address = '192.168.1.1',    raw = True)
    >>> i42 = Test_IP4_Address (address = '192.168.1.2',    raw = True)
    >>> i43 = Test_IP4_Address (address = '192.168.1.20',   raw = True)
    >>> i40.address
    192.168.0.1
    >>> i41.address
    192.168.1.1
    >>> i42.address
    192.168.1.2
    >>> i43.address
    192.168.1.20

    >>> n41 = Test_IP4_Network (address = '192.168.1.0/28', raw = True)
    >>> n42 = Test_IP4_Network (address = '192.168.1.0/29', raw = True)
    >>> n43 = Test_IP4_Network (address = '192.168.1.8/29', raw = True)
    >>> n44 = Test_IP4_Network (address = '192.168.2.0/28', raw = True)
    >>> n45 = Test_IP4_Network (address = '192.168.1.0/27', raw = True)
    >>> n46 = Test_IP4_Network (address = '192.168.0.0/27', raw = True)
    >>> n41.address
    192.168.1.0/28
    >>> n42.address
    192.168.1.0/29
    >>> n43.address
    192.168.1.8/29
    >>> n44.address
    192.168.2.0/28
    >>> n45.address
    192.168.1.0/27
    >>> n46.address
    192.168.0.0/27
    >>> scope.commit ()

    >>> address = i41.address
    >>> network = n41.address
    >>> Test_IP4_Address.query (Q.address == address).count ()
    1
    >>> Test_IP4_Address.query (Q.address != address).count ()
    3
    >>> Test_IP4_Address.query (Q.address >= address).count ()
    3
    >>> Test_IP4_Address.query (Q.address >  address).count ()
    2
    >>> Test_IP4_Address.query (Q.address <  address).count ()
    1
    >>> Test_IP4_Address.query (Q.address <= address).count ()
    2

    >>> Test_IP4_Address.query (Q.address.mask == 27).count ()
    Traceback (most recent call last):
      ...
    AttributeError: mask

    >>> Test_IP4_Address.query (Q.address.mask_len == 27).count ()
    0

    >>> Test_IP4_Address.query (Q.address.mask_len <  27).count ()
    0

    >>> Test_IP4_Address.query (Q.address.mask_len >  27).count ()
    4

    >>> Test_IP4_Network.query (Q.address.mask_len == 27).count ()
    2

    >>> Test_IP4_Network.query (Q.address.mask_len <  27).count ()
    0

    >>> Test_IP4_Network.query (Q.address.mask_len >  27).count ()
    4

    >>> Test_IP4_Address.query (Q.address.IN ("192.168.1.0/28")).count ()
    2

    >>> Test_IP4_Address.query (Q.address.IN (network)).count ()
    2

    >>> Test_IP4_Network.query (Q.address.IN ("192.168.1.0/27")).count ()
    4

    >>> Test_IP4_Network.query (Q.address.IN ("192.168.1.0/28")).count ()
    3

    >>> Test_IP4_Network.query (Q.address.IN ("192.168.1.0/29")).count ()
    1

    >>> Test_IP4_Network.query (Q.address.IN (network)).count ()
    3
    >>> r = Test_IP4_Network.query (Q.address.IN (network)).all ()
    >>> list (sorted (x.address for x in r))
    [192.168.1.0/28, 192.168.1.0/29, 192.168.1.8/29]

    >>> n42a = n42.address
    >>> Test_IP4_Network.query (Q.address.CONTAINS (n42a)).count ()
    3
    >>> i42a = i42.address
    >>> Test_IP4_Network.query (Q.address.CONTAINS (i42a)).count ()
    3

    >>> Test_IP4_Network.query (Q.address == network).count ()
    1
    >>> Test_IP4_Network.query (Q.address != network).count ()
    5
    >>> Test_IP4_Network.query (Q.address >= network).count ()
    4
    >>> Test_IP4_Network.query (Q.address >  network).count ()
    3
    >>> Test_IP4_Network.query (Q.address <  network).count ()
    2
    >>> Test_IP4_Network.query (Q.address <= network).count ()
    3

    >>> for a, m in Test_IP4_Network.query ().order_by ("-address.mask_len", "address").attrs ("address", "address.mask_len") :
    ...     print (a, m)
    192.168.1.0/29 29
    192.168.1.8/29 29
    192.168.1.0/28 28
    192.168.2.0/28 28
    192.168.0.0/27 27
    192.168.1.0/27 27

    >>> i60 = Test_IP6_Address (address = '2001:db7::1',      raw = True)
    >>> i61 = Test_IP6_Address (address = '2001:db8::1',      raw = True)
    >>> i62 = Test_IP6_Address (address = '2001:db8::2',      raw = True)
    >>> i63 = Test_IP6_Address (address = '2001:db8::20',     raw = True)
    >>> i60.address
    2001:db7::1
    >>> i61.address
    2001:db8::1
    >>> i62.address
    2001:db8::2
    >>> i63.address
    2001:db8::20

    >>> n61 = Test_IP6_Network (address = '2001:db8::/124',   raw = True)
    >>> n62 = Test_IP6_Network (address = '2001:db8::/125',   raw = True)
    >>> n63 = Test_IP6_Network (address = '2001:db8::8/125',  raw = True)
    >>> n64 = Test_IP6_Network (address = '2001:db8::10/124', raw = True)
    >>> n65 = Test_IP6_Network (address = '2001:db8::/123',   raw = True)
    >>> n66 = Test_IP6_Network (address = '2001:db7::/123',   raw = True)
    >>> n61.address
    2001:db8::/124
    >>> n62.address
    2001:db8::/125
    >>> n63.address
    2001:db8::8/125
    >>> n64.address
    2001:db8::10/124
    >>> n65.address
    2001:db8::/123
    >>> n66.address
    2001:db7::/123
    >>> scope.commit ()

    >>> Test_IP6_Address.query (Q.address.mask_len == 124).count ()
    0

    >>> Test_IP6_Address.query (Q.address.mask_len <  124).count ()
    0

    >>> Test_IP6_Address.query (Q.address.mask_len >  124).count ()
    4

    >>> Test_IP6_Network.query (Q.address.mask_len == 124).count ()
    2

    >>> Test_IP6_Network.query (Q.address.mask_len <  124).count ()
    2

    >>> Test_IP6_Network.query (Q.address.mask_len >  124).count ()
    2

    >>> address = i61.address
    >>> network = n61.address
    >>> Test_IP6_Address.query (Q.address == address).count ()
    1
    >>> Test_IP6_Address.query (Q.address != address).count ()
    3
    >>> Test_IP6_Address.query (Q.address >= address).count ()
    3
    >>> Test_IP6_Address.query (Q.address >  address).count ()
    2
    >>> Test_IP6_Address.query (Q.address <  address).count ()
    1
    >>> Test_IP6_Address.query (Q.address <= address).count ()
    2

    >>> Test_IP6_Address.query (Q.address.IN (network)).count ()
    2

    >>> Test_IP6_Network.query (Q.address.IN (network)).count ()
    3
    >>> r = Test_IP6_Network.query (Q.address.IN (network)).all ()
    >>> list (sorted (x.address for x in r))
    [2001:db8::/124, 2001:db8::/125, 2001:db8::8/125]

    >>> n62a = n62.address
    >>> Test_IP6_Network.query (Q.address.CONTAINS (n62a)).count ()
    3
    >>> i62a = i62.address
    >>> Test_IP6_Network.query (Q.address.CONTAINS (i62a)).count ()
    3


    >>> Test_IP6_Network.query (Q.address == network).count ()
    1
    >>> Test_IP6_Network.query (Q.address != network).count ()
    5
    >>> Test_IP6_Network.query (Q.address >= network).count ()
    4
    >>> Test_IP6_Network.query (Q.address >  network).count ()
    3
    >>> Test_IP6_Network.query (Q.address <  network).count ()
    2
    >>> Test_IP6_Network.query (Q.address <= network).count ()
    3

    >>> qd  = dict (address = '192.168.1.8/29')
    >>> rqs = Test_IP4_Network.raw_query_attrs (qd, qd)
    >>> rqs
    (Q.address == 192.168.1.8/29,)
    >>> type (rqs [0].rhs)
    <class 'rsclib.IP_Address.IP4_Address'>
    >>> matches = Test_IP4_Network.query_s (* rqs).all ()
    >>> print ("\n".join (repr (x) for x in matches))
    GTW.OMP.NET.Test_IP4_Network ("192.168.1.8/29")

    >>> matches2 = Test_IP4_Network.query_s (Q.address == n43.address).all ()
    >>> print ("\n".join (repr (x) for x in matches2))
    GTW.OMP.NET.Test_IP4_Network ("192.168.1.8/29")

"""

_test_qx_pg = """
    >>> from _GTW.__test__.SAW_QX import QX, show_qx as show
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> ET = apt ["GTW.OMP.NET.Test_IP4_Address"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxa = QX.Mapper (qrt)

    >>> show (qxa (Q.address == "192.168.1.0/28"))
    Bin:__eq__:
      <GTW.OMP.NET.Test_IP4_Address | QX._QX_CIDR_ for
           <SAW : IP4-address `address` [gtw_omp_net_test_ip4_address.address]>>
      192.168.1.0/28

    >>> show (qxa (Q.address.IN ("192.168.1.0/28")))
    Call:in_:
      <GTW.OMP.NET.Test_IP4_Address | QX._QX_CIDR_ for
           <SAW : IP4-address `address` [gtw_omp_net_test_ip4_address.address]>>

    >>> from _GTW.__test__._SAW_test_functions import show_query
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope ...

    >>> NET = scope.GTW.OMP.NET
    >>> Test_IP4_Address = NET.Test_IP4_Address
    >>> Test_IP4_Network = NET.Test_IP4_Network
    >>> Test_IP6_Address = NET.Test_IP6_Address
    >>> Test_IP6_Network = NET.Test_IP6_Network
    >>> n41 = Test_IP4_Network (address = '192.168.1.0/28', raw = True)
    >>> network = n41.address

    >>> show_query (Test_IP4_Address.query (Q.address.IN (n41)))
    SQL: SELECT
           gtw_omp_net_test_ip4_address.address AS gtw_omp_net_test_ip4_address_address,
           gtw_omp_net_test_ip4_address.pid AS gtw_omp_net_test_ip4_address_pid,
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked
         FROM mom_id_entity
           JOIN gtw_omp_net_test_ip4_address ON mom_id_entity.pid = gtw_omp_net_test_ip4_address.pid
         WHERE gtw_omp_net_test_ip4_address.address <<= :address_1
    Parameters:
         address_1            : GTW.OMP.NET.Test_IP4_Network ("192.168.1.0/28")

    >>> show_query (Test_IP4_Address.query (Q.address.IN ("192.168.23.0/28")))
    SQL: SELECT
           gtw_omp_net_test_ip4_address.address AS gtw_omp_net_test_ip4_address_address,
           gtw_omp_net_test_ip4_address.pid AS gtw_omp_net_test_ip4_address_pid,
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked
         FROM mom_id_entity
           JOIN gtw_omp_net_test_ip4_address ON mom_id_entity.pid = gtw_omp_net_test_ip4_address.pid
         WHERE gtw_omp_net_test_ip4_address.address <<= :address_1
    Parameters:
         address_1            : '192.168.23.0/28'

    >>> show_query (Test_IP4_Network.query (Q.address != network))
    SQL: SELECT
           gtw_omp_net_test_ip4_network.address AS gtw_omp_net_test_ip4_network_address,
           gtw_omp_net_test_ip4_network.pid AS gtw_omp_net_test_ip4_network_pid,
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked
         FROM mom_id_entity
           JOIN gtw_omp_net_test_ip4_network ON mom_id_entity.pid = gtw_omp_net_test_ip4_network.pid
         WHERE gtw_omp_net_test_ip4_network.address != :address_1
    Parameters:
         address_1            : '192.168.1.0/28'

"""

_test_qx_sq = """
    >>> from _GTW.__test__.SAW_QX import QX, show_qx as show
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> ET = apt ["GTW.OMP.NET.Test_IP4_Address"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxa = QX.Mapper (qrt)

    >>> show (qxa (Q.address == "192.168.1.0/28"))
    Bin:__eq__:
      <GTW.OMP.NET.Test_IP4_Address | QX._QX_CIDR_ for
           <SAW : IP4-address `address` [gtw_omp_net_test_ip4_address.address, gtw_omp_net_test_ip4_address.address__numeric]>>
      192.168.1.0/28

    >>> show (qxa (Q.address.IN ("192.168.1.0/28")))
    Call:in_:
      <GTW.OMP.NET.Test_IP4_Address | QX._QX_CIDR_ for
           <SAW : IP4-address `address` [gtw_omp_net_test_ip4_address.address, gtw_omp_net_test_ip4_address.address__numeric]>>

    >>> from _GTW.__test__._SAW_test_functions import show_query
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope ...

    >>> NET = scope.GTW.OMP.NET
    >>> Test_IP4_Address = NET.Test_IP4_Address
    >>> Test_IP4_Network = NET.Test_IP4_Network
    >>> Test_IP6_Address = NET.Test_IP6_Address
    >>> Test_IP6_Network = NET.Test_IP6_Network
    >>> n41 = Test_IP4_Network (address = '192.168.1.0/28', raw = True)
    >>> network = n41.address

    >>> show_query (Test_IP4_Address.query (Q.address.IN (n41)))
    SQL: SELECT
           gtw_omp_net_test_ip4_address.address AS gtw_omp_net_test_ip4_address_address,
           gtw_omp_net_test_ip4_address.address__numeric AS gtw_omp_net_test_ip4_address_address__numeric,
           gtw_omp_net_test_ip4_address.pid AS gtw_omp_net_test_ip4_address_pid,
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked
         FROM mom_id_entity
           JOIN gtw_omp_net_test_ip4_address ON mom_id_entity.pid = gtw_omp_net_test_ip4_address.pid
         WHERE gtw_omp_net_test_ip4_address.address__numeric >= :address__numeric_1
            AND gtw_omp_net_test_ip4_address.address__numeric <= :address__numeric_2
    Parameters:
         address__numeric_1   : 1084752128
         address__numeric_2   : 1084752143

    >>> show_query (Test_IP4_Address.query (Q.address.IN ("192.168.23.0/28")))
    SQL: SELECT
           gtw_omp_net_test_ip4_address.address AS gtw_omp_net_test_ip4_address_address,
           gtw_omp_net_test_ip4_address.address__numeric AS gtw_omp_net_test_ip4_address_address__numeric,
           gtw_omp_net_test_ip4_address.pid AS gtw_omp_net_test_ip4_address_pid,
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked
         FROM mom_id_entity
           JOIN gtw_omp_net_test_ip4_address ON mom_id_entity.pid = gtw_omp_net_test_ip4_address.pid
         WHERE gtw_omp_net_test_ip4_address.address__numeric >= :address__numeric_1
            AND gtw_omp_net_test_ip4_address.address__numeric <= :address__numeric_2
    Parameters:
         address__numeric_1   : 1084757760
         address__numeric_2   : 1084757775

    >>> show_query (Test_IP4_Network.query (Q.address != network))
    SQL: SELECT
           gtw_omp_net_test_ip4_network.address AS gtw_omp_net_test_ip4_network_address,
           gtw_omp_net_test_ip4_network.address__mask_len AS gtw_omp_net_test_ip4_network_address__mask_len,
           gtw_omp_net_test_ip4_network.address__numeric AS gtw_omp_net_test_ip4_network_address__numeric,
           gtw_omp_net_test_ip4_network.address__upper_bound AS gtw_omp_net_test_ip4_network_address__upper_bound,
           gtw_omp_net_test_ip4_network.pid AS gtw_omp_net_test_ip4_network_pid,
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked
         FROM mom_id_entity
           JOIN gtw_omp_net_test_ip4_network ON mom_id_entity.pid = gtw_omp_net_test_ip4_network.pid
         WHERE gtw_omp_net_test_ip4_network.address__numeric != :address__numeric_1
            OR gtw_omp_net_test_ip4_network.address__mask_len != :address__mask_len_1
    Parameters:
         address__mask_len_1  : 28
         address__numeric_1   : 1084752128


"""

_test_debug = """
    >>> from _GTW.__test__._SAW_test_functions import show_query
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    >>> NET = scope.GTW.OMP.NET
    >>> Test_IP4_Address = NET.Test_IP4_Address
    >>> Test_IP4_Network = NET.Test_IP4_Network
    >>> Test_IP6_Address = NET.Test_IP6_Address
    >>> Test_IP6_Network = NET.Test_IP6_Network

    >>> i40 = Test_IP4_Address (address = '192.168.0.1',    raw = True)
    >>> n41 = Test_IP4_Network (address = '192.168.1.0/28', raw = True)
    >>> network = n41.address


    >>> Test_IP4_Network.query (Q.address != network).count ()

"""

from _GTW.__test__.model import *

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_ip4   = _test_ip4
        , test_ip6   = _test_ip6
        , test_mac   = _test_mac
        , test_query = _test_query
        )
    )

__test__.update \
    ( Scaffold.create_test_dict
        ( dict
            ( test_qx_pg = _test_qx_pg
            )
        , ignore = ("HPS", "MYS", "SQL", "sq")
        )
    )

__test__.update \
    ( Scaffold.create_test_dict
        ( dict
            ( test_qx_sq = _test_qx_sq
            )
        , ignore = ("HPS", "MYS", "POS", "pg")
        )
    )

X__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_debug     = _test_debug
        )
    )

### __END__ GTW.__test__.Attr_Net
