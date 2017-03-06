# coding: latin-1

###############################################################################
# eVotUM - Electronic Voting System
#
# pbkdf2.py
#
# Cripto-8.0.0 - PBKDF2
#
# Copyright (c) 2016 Universidade do Minho
# Developed by André Baptista - Devise Futures, Lda. (andre.baptista@devisefutures.com)
# Reviewed by Ricardo Barroso - Devise Futures, Lda. (ricardo.barroso@devisefutures.com)
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
###############################################################################

"""
PBKDF2 applies a pseudorandom function (SHA256 hash function) to the input password or passphrase
along with a salt value (32 bytes salt value, generated with os.urandom for each derived key)
and repeats the process many times (100.000 iterations) to produce a derived key,
which can then be used as a cryptographic key in subsequent operations.
The added computational work makes password cracking much more difficult, and is known as
key stretching.
"""

from eVotUM.Cripto import utils

from Crypto.Hash import SHA256

KDF_SALT_BYTES_LENGTH = 32
KDF_N_ITERATIONS = 100000

def kdf(password, salt):
    sha256Hash = SHA256.new()
    derivedKey = password
    for i in range(KDF_N_ITERATIONS):
        derivedKey += salt + str(i)
        sha256Hash.update(derivedKey)
        derivedKey = sha256Hash.hexdigest()
    return derivedKey


# Cripto-8.1.0
def generatePBKDF(password):
    """
    Generate derived Key.

    Args:
        password (str): password or passphrase
    Returns:
        tuple with [derived key (hex), salt (hex)].
    """
    salt = utils.generateRandomData(KDF_SALT_BYTES_LENGTH).encode("hex")
    derivedKey = kdf(password, salt)
    return derivedKey, salt

# Cripto-8.2.0
def verifyPBKDF(password, derivedKey, salt):
    """
    Validate password.

    Args:
        password (str): password or passphrase to be validated
        derivedKey (hex): derived key to be validated
        salt (hex): salt value generated for derivedKey
    Returns:
        True if PBKDF2 (password, salt) == derivedKey; False otherwise
    """
    return (kdf(password, salt) == derivedKey)
