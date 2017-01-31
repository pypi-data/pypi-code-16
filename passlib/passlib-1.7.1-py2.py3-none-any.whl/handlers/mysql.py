"""passlib.handlers.mysql

MySQL 3.2.3 / OLD_PASSWORD()

    This implements Mysql's OLD_PASSWORD algorithm, introduced in version 3.2.3, deprecated in version 4.1.

    See :mod:`passlib.handlers.mysql_41` for the new algorithm was put in place in version 4.1

    This algorithm is known to be very insecure, and should only be used to verify existing password hashes.

    http://djangosnippets.org/snippets/1508/

MySQL 4.1.1 / NEW PASSWORD
    This implements Mysql new PASSWORD algorithm, introduced in version 4.1.

    This function is unsalted, and therefore not very secure against rainbow attacks.
    It should only be used when dealing with mysql passwords,
    for all other purposes, you should use a salted hash function.

    Description taken from http://dev.mysql.com/doc/refman/6.0/en/password-hashing.html
"""
#=============================================================================
# imports
#=============================================================================
# core
from hashlib import sha1
import re
import logging; log = logging.getLogger(__name__)
from warnings import warn
# site
# pkg
from passlib.utils import to_native_str
from passlib.utils.compat import bascii_to_str, unicode, u, \
                                 byte_elem_value, str_to_uascii
import passlib.utils.handlers as uh
# local
__all__ = [
    'mysql323',
    'mysq41',
]

#=============================================================================
# backend
#=============================================================================
class mysql323(uh.StaticHandler):
    """This class implements the MySQL 3.2.3 password hash, and follows the :ref:`password-hash-api`.

    It has no salt and a single fixed round.

    The :meth:`~passlib.ifc.PasswordHash.hash` and :meth:`~passlib.ifc.PasswordHash.genconfig` methods accept no optional keywords.
    """
    #===================================================================
    # class attrs
    #===================================================================
    name = "mysql323"
    checksum_size = 16
    checksum_chars = uh.HEX_CHARS

    #===================================================================
    # methods
    #===================================================================
    @classmethod
    def _norm_hash(cls, hash):
        return hash.lower()

    def _calc_checksum(self, secret):
        # FIXME: no idea if mysql has a policy about handling unicode passwords
        if isinstance(secret, unicode):
            secret = secret.encode("utf-8")

        MASK_32 = 0xffffffff
        MASK_31 = 0x7fffffff
        WHITE = b' \t'

        nr1 = 0x50305735
        nr2 = 0x12345671
        add = 7
        for c in secret:
            if c in WHITE:
                continue
            tmp = byte_elem_value(c)
            nr1 ^= ((((nr1 & 63)+add)*tmp) + (nr1 << 8)) & MASK_32
            nr2 = (nr2+((nr2 << 8) ^ nr1)) & MASK_32
            add = (add+tmp) & MASK_32
        return u("%08x%08x") % (nr1 & MASK_31, nr2 & MASK_31)

    #===================================================================
    # eoc
    #===================================================================

#=============================================================================
# handler
#=============================================================================
class mysql41(uh.StaticHandler):
    """This class implements the MySQL 4.1 password hash, and follows the :ref:`password-hash-api`.

    It has no salt and a single fixed round.

    The :meth:`~passlib.ifc.PasswordHash.hash` and :meth:`~passlib.ifc.PasswordHash.genconfig` methods accept no optional keywords.
    """
    #===================================================================
    # class attrs
    #===================================================================
    name = "mysql41"
    _hash_prefix = u("*")
    checksum_chars = uh.HEX_CHARS
    checksum_size = 40

    #===================================================================
    # methods
    #===================================================================
    @classmethod
    def _norm_hash(cls, hash):
        return hash.upper()

    def _calc_checksum(self, secret):
        # FIXME: no idea if mysql has a policy about handling unicode passwords
        if isinstance(secret, unicode):
            secret = secret.encode("utf-8")
        return str_to_uascii(sha1(sha1(secret).digest()).hexdigest()).upper()

    #===================================================================
    # eoc
    #===================================================================

#=============================================================================
# eof
#=============================================================================
