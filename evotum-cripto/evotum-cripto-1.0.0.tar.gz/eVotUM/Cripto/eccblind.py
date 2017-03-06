# coding: latin-1

###############################################################################
# eVotUM - Electronic Voting System
#
# eccblind.py
#
# Cripto-7.0.0 - Blind signatures
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
In cryptography, a blind signature is a form of digital signature in which the content of
a message is disguised (blinded) before it is signed. The resulting blind signature can be
publicly verified against the original, unblinded message in the manner of a regular digital
signature.
Blind signatures are typically employed in privacy-related protocols where the signer and
message author are different parties. Examples include cryptographic election systems and
digital cash schemes.

An often-used analogy to the cryptographic blind signature is the physical act of a voter
enclosing a completed anonymous ballot in a special carbon paper lined envelope that has
the voter's credentials pre-printed on the outside. The ballot can be marked through the
envelope by the carbon paper. The voter hands the sealed envelope to an official who verifies
the credentials and signs it. Once signed, the package is given back to the voter, who
transfers the now signed ballot to a new unmarked normal envelope. Thus, the signer does
not view the message content, but a third party can later verify the signature and know
that the signature is valid within the limitations of the underlying signature scheme.

Blind signatures can also be used to provide unlinkability, which prevents the signer from
linking the blinded message it signs to a later un-blinded version that it may be called upon
to verify. In this case, the signer's response is first "un-blinded" prior to verification in
such a way that the signature remains valid for the un-blinded message. This can be useful in
schemes where anonymity is required.
(in Wikipedia https://en.wikipedia.org/wiki/Blind_signature)

This implementation of blind signatures follows the paper by Aye Aye Thu and Khin Than Mya
(Implementation of an Efficient Blind Signature Scheme - http://www.ijimt.org/papers/556-IT302.pdf),
but using SHA256 instead of SHA-1.
"""

from eVotUM.Cripto import utils
from eVotUM.Cripto import hashfunctions

from Crypto.PublicKey import ECC
from Crypto.Math.Numbers import Integer
from Crypto.Util import number

CURVE_N = ECC._curve.order
CURVE_G = ECC._curve.G

#math functions
def getCurveOrderRandom():
    return Integer.random_range(min_inclusive=1, max_exclusive=CURVE_N)

def init():
    while (True):
        k = getCurveOrderRandom()
        pRDash = CURVE_G * k
        rDash = pRDash.x % CURVE_N
        if (rDash != 0):
            return pRDash, rDash, k

def blind(pRDash, h):
    rDash = pRDash.x % CURVE_N

    v = getCurveOrderRandom()
    pR = pRDash * v.inverse(CURVE_N)
    r = pR.x % CURVE_N

    blindM = (h * r.inverse(CURVE_N) * rDash * v) % CURVE_N
    return blindM, v, pR, r

def sign(d, blindM, rDash, k):
    return d * blindM + ((k * rDash) % CURVE_N)

def unblind(s, v, rDash, r):
    return (s * v.inverse(CURVE_N) * rDash.inverse(CURVE_N) * r) % CURVE_N

def verify(sDash, pointQ, h, pR, r):
    return ((CURVE_G * sDash) == ((pointQ * h) + (pR * r)))

#mainFunctions
#Cripto 7.0.1
def initSigner():
    """
    Initialization of the blind signature scheme, according to section IV.A of the
    paper followed in this implementation.

    Args:
        none
    Returns:
        initComponents (str), pRDashComponents (str): initComponents = "r' (hex) . k (hex)" and
            pRDashComponents = "R' x coordinate (hex) . R' y coordinate (hex)"
    """
    pRDash, rDash, k = init()
    return pack([rDash, k]), pack([pRDash.x, pRDash.y])

#Cripto 7.1.0
def blindData(pRDashComponents, data):
    """
    Blinds data, according to section IV.B of the paper followed in this implementation.

    Args:
        pRDashComponents (str): pRDashComponents returned by initSigner()
        data (str): data to be blinded
    Returns:
        errorCode (int/None), [blindComponents (str), pRComponents (str), blindMessage (hex)]: if errorCode
            is None, the components of the list  have the following values: blindComponents = "v (hex) . r (hex)",
            pRComponents = "R x coordinate (hex) . R y coordinate (hex)" and BlindMessage = m' (hex). If
            errorCode is not None, the list is None.
            The errorCode has the following meaning:
                1 - invalid format of pRDashComponents
    """
    pRDash = unpackEccPoint(pRDashComponents)
    if (pRDash is None):
        return 1, None

    h = hexToInteger(hashfunctions.generateSHA256Hash(data))
    blindM, v, pR, r = blind(pRDash, h)

    return None, [pack([v, r]), pack([pR.x, pR.y]), integerToHex(blindM)]

#Cripto 7.2.0
def generateBlindSignature(pemKey, passphrase, blindM, initComponents):
    """
    Signs blindM (blind data), according to section IV.C of the paper followed in this implementation.

    Args:
        pemKey (PEM): signer's private key in PEM format
        passphrase (str): passphrase to access pemKey
        blindM (hex): blind message that will be signed, returned by blindData()
        initComponents (str): initComponents returned by initSigner()
    Returns:
        errorCode (int/None), blindSignature (hex/None): tuple with error code and blind signature of blindM.
            The errorCode has the following meaning:
                1 - it was not possible to retrieve the private key from pemKey
                2 - invalid format of initComponents
                3 - invalid format of blindM
            If the errorCode is not None, blindSignature will be None
    """
    errorCode, privateKey = getKey(pemKey, passphrase)
    if (errorCode is not None):
        return 1, None

    result = unpack(initComponents)
    if (result is None or len(result) != 2):
        return 2, None

    rDash, k = result

    intBlindM = hexToInteger(blindM)
    if (intBlindM is None):
        return 3, None

    return None, integerToHex(sign(privateKey.d, intBlindM, rDash, k))

#Cripto 7.3.0
def unblindSignature(blindSignature, pRDashComponents, blindComponents):
    """
    Unblinds blindSignature, according to section IV.D of the paper followed in this implementation,
    meaning that this function returns the signature of data (see blindData()) by pemKey (see generateBlindSignature())

    Args:
        blindSignature (hex): blind signature that will be unblinded, returned by generateBlindSignature()
        pRDashComponents (str): pRDashComponents returned by initSigner()
        blindComponents (str): blindComponents returned by blindData()
    Returns:
        errorCode (int/None), signature (hex/None): tuple with errorCode and
        unblinded blindSignature, meaning the signature of data (see blindData()) by pemKey (see generateBlindSignature()).
            The errorCode has the following meaning:
                1 - invalid format of pRDashComponents
                2 - invalid format of blindComponents
                3 - invalid format of blindSignature
            If the errorCode is not None, signature will be None
    """
    pRDash = unpackEccPoint(pRDashComponents)
    if (pRDash is None):
        return 1, None

    result = unpack(blindComponents)
    if (result is None or len(result) != 2):
        return 2, None

    v, r = result

    rDash = pRDash.x % CURVE_N

    intBlindSignature = hexToInteger(blindSignature)
    if (intBlindSignature is None):
        return 3, None

    return None, integerToHex(unblind(intBlindSignature, v, rDash, r))

#Cripto 7.4.0
def verifySignature(pemPublicKey, signature, blindComponents, pRComponents, data):
    """
    Verify signature of data, according to section IV.E of the paper followed in this implementation,
    meaning that this function verifies if signature is the signature of data
    Note that to get the public key from a certificate, you should use importKey(pemCertificatePath) or
    getKey(pemCertificate)

    Args:
        pemPublicKey (PEM): signer's public key in PEM format
        signature (hex): signature to verify, returned by unblindSignature()
        blindComponents (str): blindComponents returned by blindData()
        pRComponents (str): pRDashComponents returned by blindData()
        data (str): data blinded in blindData()
    Returns:
        errorCode (int/None), verified (bool/None): tuple with errorCode and verified (True if signature is
        the signature of data; False otherwise).
            The errorCode has the following meaning:
                1 - invalid format of public key
                2 - invalid format of pRComponents
                3 - invalid format of blindComponents
                4 - invalid format of signature
            If the errorCode is not None, verified will be None
    """
    errorCode, publicKey = getKey(pemPublicKey)
    if (errorCode == 1):
        return 1, None

    pR = unpackEccPoint(pRComponents)
    if (pR is None):
        return 2, None

    h = hexToInteger(hashfunctions.generateSHA256Hash(data))

    result = unpack(blindComponents)
    if (result is None or len(result) != 2):
        return 3, None

    v, r = result

    intSignature = hexToInteger(signature)
    if (intSignature is None):
        return 4, None

    return None, verify(intSignature, publicKey.pointQ, h, pR, r)

#import/export
def importKey(path, passphrase = None):
    pemKey = utils.readFile(path)
    return getKey(pemKey, passphrase)

def getKey(pemKey, passphrase = None):
    try:
        return None, ECC.import_key(pemKey, passphrase)
    except:
        return 1, None

#utils
def pack(l):
    try:
        return ".".join(map(lambda x:integerToHex(x), l))
    except:
        return None

def unpack(s):
    try:
        return map(lambda x:hexToInteger(x), s.split("."))
    except:
        return None

def unpackEccPoint(s):
    l = unpack(s)

    if (l is None or len(l) != 2):
        return None

    return ECC.EccPoint(l[0], l[1])

def integerToHex(n):
    s = hex(int(n))[2:]
    if (s[-1:] == "L"):
        s = s[:-1]
    return s

def hexToInteger(s):
    try:
        return Integer(int(s, 16))
    except:
        return None
