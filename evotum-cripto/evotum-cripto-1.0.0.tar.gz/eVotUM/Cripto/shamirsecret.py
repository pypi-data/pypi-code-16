# coding: latin-1

###############################################################################
# eVotUM - Electronic Voting System
#
# shamirsecret.py
#
# Cripto-4.0.0 - Shamir Secret sharing Functions
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
Shamir's Secret Sharing is a cryptographic algorithm created by Adi Shamir.
It's a form of secret sharing, where a secret is divided into n parts, giving each
participant its own unique part, where some of the parts or all of them are needed
in order to reconstruct the secret.

Counting on all participants to combine the secret might be impractical, and
therefore sometimes the threshold scheme is used where any k (quorum) of the n parts are
sufficient to reconstruct the original secret.
"""

from eVotUM.Cripto import utils
from eVotUM.Cripto import pkiutils
from eVotUM.Cripto import hashfunctions

from secretsharing import SecretSharer

import string, time

SECRET_MAX_BYTES_LENGTH = 64
MAX_SHARES = 24
MIN_SHARES = 2 #required by secretsharing python library

#Cripto-4.1.0
def createSharedSecretComponents(secret, nShares, quorum, uid, pemPrivateKey, keyPassphrase):
    """
    This function divides the secret (with max length of SECRET_MAX_BYTES_LENGTH)
    into nShares parts (using Shamir's Secret Sharing algorithm), where any quorum
    of the parts are sufficient to reconstruct the original secret.
    Returns a list with nShares components, where each component is a JWT (JSON
    Web Signature) object signed by pemPrivateKey, containing a part of the secret (share),
    uid, quorum, nShares and a hash (SHA256) of the share + uid + quorum + nShares, i.e.,
    each signed JWT object contains (share, uid, quorum, nShares, SHA256(share + uid + quorum + nShares)).
    Note that this function does not verify if pemPrivateKey is a well formed PEM private key, or if
    keyPassphrase 'opens' the access to the private key. For that, use other functions.
    Args:
        secret (str): secret to be divided into nShares parts
        nShares (int): number of parts the secret is divided into (MIN_SHARES <= nShares <= MAX_SHARES)
        quorum (int): minimum number of the parts necessary to reconstruct the original secret (MIN_SHARES <= quorum <= nShares)
        uid (str): usage id of the secret (should be unique)
        pemPrivateKey (pem): private key (in PEM format) used to sign ech JWT component of the returned list
        keyPassphrase (str): passphrase to access the private key
    Returns:
        errorCode (int/None), [JWT object (base64)]: tuple with error code and JSON Web Signature (JWS) list.
            The errorCode has the following meaning:
                None - JWS list was created with success
                1 - one of the JWS objects could not be created by pkiutils.signObject
                11 - secret length > SECRET_MAX_BYTES_LENGTH
                12 - quorom < MIN_SHARES
                13 - quorum > nShares
                14 - nShares > MAX_SHARES
            If the errorCode is not None, JWT will be None
    """
    if (len(secret) > SECRET_MAX_BYTES_LENGTH):
        return 11, None
    if (quorum < MIN_SHARES):
        return 12, None
    if (quorum > nShares):
        return 13, None
    if (nShares > MAX_SHARES):
        return 14, None

    shamirSecretShares = SecretSharer.split_secret(secret.encode("hex"), quorum, nShares)

    shamirSecretComponents = []
    for share in shamirSecretShares:
        sha256Hash = hashfunctions.generateSHA256Hash("%s%s%s%s" % (share, uid, quorum, nShares))
        errorCode, jwt = pkiutils.signObject([share, uid, quorum, nShares, sha256Hash], pemPrivateKey, keyPassphrase)
        if (jwt is None):
            return errorCode, jwt
        shamirSecretComponents.append(jwt)
    return None, shamirSecretComponents

#Cripto-4.2.0
def recoverSecretFromComponents(shamirSecretComponents, uid, pemCertificate, allComponents = False):
    """
    This function recovers the secret from its components/parts and verifies that
    all the components have the same usage id (uid) and uses pemCertificate to verify
    its signature.
    Returns the secret.
    Args:
        shamirSecretComponents ([JWT object (base64)]): list with at least the minimum components/parts to recover the secret;
        uid (str): usage id of the secret
        pemCertificate (pem): certificate (in PEM format) used to verify each element of shamirSecretComponents
        allComponents (boolean): check if all the components are present
    Returns:
        errorCode (int/None), secret (str): tuple with error code and secret.
            The errorCode has the following meaning:
                None - secret was recovered with success
                1 - pemCertificate is not within the validity period
                2 - pemCertificate format is invalid (not PEM)
                3 - it was not possible to retrieve the public key from pemCertificate
                4 - one of the elements of shamirSecretComponents is not well formated
                    or was not signed with the private key associated to the public key
                    in pemCertificate
                10 - there are repeated components
                11 - the number of shares is less than quorum
                12 - one of the elements of shamirSecretComponents has not the
                    usage id uid
                13 - the recovered secret has an invalid length
                14 - invalid number of components
                15 - invalid hash
            If the errorCode is not None, secret will be None
    """
    if (hasRepeatedElements(shamirSecretComponents)):
        return 10, None

    shamirSecretShares = []

    for jwt in shamirSecretComponents:
        errorCode, obj = pkiutils.verifyObjectSignature(jwt, pemCertificate)
        if (errorCode > 0):
            return errorCode, None

        [share, tmpUID, quorum, nShares, sha256Hash] = obj

        if (sha256Hash != hashfunctions.generateSHA256Hash("%s%s%s%s" % (share, tmpUID, quorum, nShares))):
            #Invalid hash found in one of the components
            return 15, None

        if (uid != tmpUID):
            #Invalid uid found in one of the components
            return 12, None

        if (len(shamirSecretComponents) < quorum):
            #The number of shares is less than quorum
            return 11, None

        if (allComponents):
            if (len(shamirSecretComponents) != nShares):
                #Invalid number of components
                return 14, None

        shamirSecretShares.append(share)

    hexSecret = SecretSharer.recover_secret(shamirSecretShares)

    secret = hexSecret.decode("hex")

    if (len(secret) <= SECRET_MAX_BYTES_LENGTH):
        return None, secret
    else:
        #The recovered secret has an invalid length
        return 13, None

#Cripto-4.2.2
def recoverSecretFromAllComponents(shamirSecretComponents, uid, pemCertificate):
    """
    This function recovers the secret from all its components/parts and verifies that
    all the components have the same usage id (uid) and uses pemCertificate to verify
    its signature.
    Returns the secret.
    Args:
        shamirSecretComponents ([JWT object (base64)]): list with all the components/parts to recover the secret;
        uid (str): usage id of the secret
        pemCertificate (pem): certificate (in PEM format) used to verify each element of shamirSecretComponents
    Returns:
        errorCode (int/None), secret (str): tuple with error code and secret.
            The errorCode has the following meaning:
                None - secret was recovered with success
                1 - pemCertificate is not within the validity period
                2 - pemCertificate format is invalid (not PEM)
                3 - it was not possible to retrieve the public key from pemCertificate
                4 - one of the elements of shamirSecretComponents is not well formated
                    or was not signed with the private key associated to the public key
                    in pemCertificate
                10 - there are repeated components
                11 - the number of shares is less than quorum
                12 - one of the elements of shamirSecretComponents has not the
                    usage id uid
                13 - the recovered secret has an invalid length
                14 - invalid number of components
                15 - invalid hash
            If the errorCode is not None, secret will be None
    """
    return recoverSecretFromComponents(shamirSecretComponents, uid, pemCertificate, allComponents = True)

#Cripto-4.3.0
def createSecretComponents(secretLength, nShares, quorum, uid, pemPrivateKey, keyPassphrase):
    """
    This function generates the secret (with secretLength <= SECRET_MAX_BYTES_LENGTH characters)
    and divides it into nShares parts (using Shamir's Secret Sharing algorithm), where any quorum
    of the parts are sufficient to reconstruct the original secret.
    Returns a list with nShares components, where each component is a JWT (JSON
    Web Signature) object signed by pemPrivateKey, containing a part of the secret (share),
    uid, quorum, nShares and a hash (SHA256) of the share + uid + quorum + nShares, i.e.,
    each signed JWT object contains (share, uid, quorum, nShares, SHA256(share + uid + quorum + nShares)).
    Note that this function does not verify if pemPrivateKey is a well formed PEM private key, or if
    keyPassphrase 'opens' the access to the private key. For that, use other functions.
    Args:
        secretLength (int): number of characters of the secret
        nShares (int): number of parts the secret is divided into (MIN_SHARES <= nShares <= MAX_SHARES)
        quorum (int): minimum number of the parts necessary to reconstruct the original secret (MIN_SHARES <= quorum <= nShares)
        uid (str): usage id of the secret (should be unique)
        pemPrivateKey (pem): private key (in PEM format) used to sign ech JWT component of the returned list
        keyPassphrase (str): passphrase to access the private key
    Returns:
        errorCode (int/None), [JWT object (base64)]: tuple with error code and JSON Web Signature (JWS) list.
            The errorCode has the following meaning:
                None - JWS list was created with success
                1 - one of the JWS objects could not be created by pkiutils.signObject
                11 - secretLength > SECRET_MAX_BYTES_LENGTH
                12 - quorom < MIN_SHARES
                13 - quorum > nShares
                14 - nShares > MAX_SHARES
            If the errorCode is not None, JWT will be None
    """
    secret = generateSecret(secretLength)
    return createSharedSecretComponents(secret, nShares, quorum, uid, pemPrivateKey, keyPassphrase)


#Cripto-4.4.0
def generateSecret(secretLength):
    """
    This function generates a random string with secretLength characters (ascii_letters and digits).
    Args:
        secretLength (int): number of characters of the string
    Returns:
        Random string with secretLength characters (ascii_letters and digits)
    """
    l = 0
    secret = ""
    while (l < secretLength):
        s = utils.generateRandomData(secretLength - l)
        for c in s:
            if (c in (string.ascii_letters + string.digits) and l < secretLength): # printable character
                l += 1
                secret += c
    return secret

#Cripto-4.5.0
def generateSecretTime(secretLength, timeToLive, chars="ABCDEFGHJKLMNPQRSTUVWXYZ23456789"):
    """
    This function generates a random string with secretLength chars and a
    validity period of timeToLive seconds.
    Args:
        secretLength (int): number of characters of the string
        timeToLive (int): validity time in seconds
        chars (str): set of characters of the generated secret
    Returns:
        secret (str), time (float): secret is a random string with secretLength chars and,
        time is the time in seconds, since the epoch as a floating point number, until when
        the secret should be considered valid
    """
    l = 0
    secret = ""
    while (l < secretLength):
        s = utils.generateRandomData(secretLength - l)
        for c in s:
            if (c in chars and l < secretLength): # printable character
                l += 1
                secret += c
    return secret, time.time() + timeToLive

#Cripto-4.6.0
def hasComponents(shamirSecretComponents, uid, pemCertificate, allComponents = False):
    """
    This function verifies if shamirSecretComponents has at least the quorum number of components
    (or all components if allComponents == True) necessary to reconstruct the secret. It also
    verifies that all the components have the same usage id (uid) and uses pemCertificate to verify
    its signature.
    Returns None/errorCode if shamirSecretComponents has/has not the expected number of components.
    Args:
        shamirSecretComponents ([JWT object (base64)]): list with at least the minimum components/parts to recover the secret;
        uid (str): usage id of the secret
        pemCertificate (pem): certificate (in PEM format) used to verify each element of shamirSecretComponents
        allComponents (boolean): check if all the components are present
    Returns:
        errorCode (int/None): errorCode has the following meaning:
                None - shamirSecretComponents has the expected number of components
                1 - pemCertificate is not within the validity period
                2 - pemCertificate format is invalid (not PEM)
                3 - it was not possible to retrieve the public key from pemCertificate
                4 - one of the elements of shamirSecretComponents is not well formated
                    or was not signed with the private key associated to the public key
                    in pemCertificate
                10 - there are repeated components
                11 - the number of shares is less than quorum
                12 - one of the elements of shamirSecretComponents has not the
                    usage id uid
                13 - the recovered secret has an invalid length
                14 - invalid number of components
                15 - invalid hash
    """
    errorCode, secret = recoverSecretFromComponents(shamirSecretComponents, uid, pemCertificate, allComponents)
    return errorCode

#Cripto-4.6.2
def hasAllComponents(shamirSecretComponents, uid, pemCertificate):
    """
    This function verifies if shamirSecretComponents has all the components in which the
    secret was divided. It also verifies that all the components have the same usage id (uid) and uses pemCertificate to verify
    its signature.
    Returns None/errorCode if shamirSecretComponents has/has not the expected number of components.
    Args:
        shamirSecretComponents ([JWT object (base64)]): list with all the components/parts to recover the secret;
        uid (str): usage id of the secret
        pemCertificate (pem): certificate (in PEM format) used to verify each element of shamirSecretComponents
    Returns:
        errorCode (int/None): errorCode has the following meaning:
                None - shamirSecretComponents has the expected number of components
                1 - pemCertificate is not within the validity period
                2 - pemCertificate format is invalid (not PEM)
                3 - it was not possible to retrieve the public key from pemCertificate
                4 - one of the elements of shamirSecretComponents is not well formated
                    or was not signed with the private key associated to the public key
                    in pemCertificate
                10 - there are repeated components
                11 - the number of shares is less than quorum
                12 - one of the elements of shamirSecretComponents has not the
                    usage id uid
                13 - the recovered secret has an invalid length
                14 - invalid number of components
                15 - invalid hash
    """
    return hasComponents(shamirSecretComponents, uid, pemCertificate, allComponents = True)


#utils
def hasRepeatedElements(list):
    for item in list:
        if (list.count(item) != 1):
            return True
    return False
