# coding: latin-1

###############################################################################
# eVotUM - Electronic Voting System
#
# cautils.py
#
# Cripto-9.0.0 - CA utils
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
This library, based on the OpenSSL library, implements and provides various CA (Certification
Authority) utility functions, namely for generating RSA key pairs and CSR (certificate requests),
for issuing certificates and, for obtaining the public key and private key from a key pair in
PEM format.
"""

from Crypto.PublicKey import RSA

import OpenSSL, time

DEFAULT_KEY_BITS_SIZE = 2048
DEFAULT_CIPHER = "AES-256-CBC"
DEFAULT_HASH_FUNCTION = "sha256"

#Cripto 9.1.0
def generateRSAKeyPair(keyBitsSize = DEFAULT_KEY_BITS_SIZE):
    """
    Generates a RSA key pair.
    Notice that you should use pKeyToPEMPrivateKey() and pKeyToPEMPublicKey() to transform the
    RSA key pair into the private and public key, respectively, in PEM format.

    Args:
        keyBitsSize (int): RSA key bit size
    Returns:
        errorCode (int/None), RSAKeyPair (PKey object/None): If errorCode is None, returns RSA key
            pair. If errorCode is not None, RSAKeyPair will be None.
            The meaning of errorCode is the following:
                1 - invalid key size.
    """
    keyPair = OpenSSL.crypto.PKey()
    try:
        keyPair.generate_key(OpenSSL.crypto.TYPE_RSA, keyBitsSize)
        return None, keyPair
    except:
        return 1, None

#Cripto 9.2.0
def generateCSR(pemPrivateKey, keyPassphrase, commonName, countryName, stateOrProvinceName, localityName, organizationName, organizationalUnitName):
    """
    Generates a certificate request (CSR) in PEM format.

    Args:
        pemPrivateKey (PEM): private key in PEM format
        keyPassphrase (str): passphrase to access the private key pemPrivateKey
        commonName (str): common name (CN) for the certificate requests
        countryName (str): two-letter country name (C) for the certificate requests
        stateOrProvinceName (str): state or province name (ST) for the certificate request
        localityName (str): locality name (L) for the certificate request
        organizationName (str): organization name (O) for the certificate request
        organizationalUnitName (str): organizational unit name (OU) for the certificate request
    Returns:
        errorCode (int/None), CSR (PEM/None): If errorCode is None, returns certificate request
            in PEM format. If errorCode is not None, CSR will be None.
            The meaning of errorCode is the following:
                1 - invalid private key format or incorrect passphrase
                2 - invalid certificate parameters
    """
    x509Request = OpenSSL.crypto.X509Req()

    errorCode, keyPair = pemPrivateKeyToPKey(pemPrivateKey, keyPassphrase)

    if (errorCode == 1):
        return 1, None

    try:
        subject = x509Request.get_subject()
        subject.CN = commonName
        subject.countryName = countryName
        subject.stateOrProvinceName = stateOrProvinceName
        subject.localityName = localityName
        subject.organizationName = organizationName
        subject.organizationalUnitName = organizationalUnitName
    except:
        return 2, None

    x509Request.set_pubkey(keyPair)
    x509Request.sign(keyPair, DEFAULT_HASH_FUNCTION)

    return None, OpenSSL.crypto.dump_certificate_request(OpenSSL.crypto.FILETYPE_PEM, x509Request)

#Cripto 9.3.0
def signCSR(pemCACertificate, pemCAPrivateKey, keyPassphrase, pemCSR, serialNumber, notBefore, notAfter):
    """
    Signs the certificate request with the CA private key, and issues the certificate.

    Args:
        pemCACertificate (PEM): CA certificate in PEM format
        pemCAPrivateKey (PEM): CA private key in PEM format
        keyPassphrase (str): passphrase to access the private key pemCAPrivateKey
        pemCSR (PEM): certificate request in PEM format
        serialNumber (int): certificate serial number (each certificate signed by a CA should have a different serial number)
        notBefore (int): adjust the timestamp (in GMT) when the certificate starts being valid, in seconds (0 = now)
        notAfter (int): adjust the timestamp (in GMT) when the certificate stops being valid, in seconds (0 = now)
    Returns:
        errorCode (int/None), cert (PEM/None): If errorCode is None, returns certificate
            in PEM format. If errorCode is not None, cert will be None.
            The meaning of errorCode is the following:
                1 - invalid CA certificate format
                2 - invalid CA private key format or incorrect passphrase
                3 - invalid certificate request format
                4 - invalid serial number
                5 - invalid timestamp (notBefore or notAfter)
    """
    try:
        x509CACertificate = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, pemCACertificate)
    except:
        return 1, None

    errorCode, caPrivateKey = pemPrivateKeyToPKey(pemCAPrivateKey, keyPassphrase)

    if (errorCode == 1):
        return 2, None

    try:
        x509Request = OpenSSL.crypto.load_certificate_request(OpenSSL.crypto.FILETYPE_PEM, pemCSR)
    except:
        return 3, None

    x509Certificate = OpenSSL.crypto.X509()
    x509Certificate.set_pubkey(x509Request.get_pubkey())

    try:
        x509Certificate.set_serial_number(serialNumber)
    except:
        return 4, None

    try:
        x509Certificate.gmtime_adj_notBefore(notBefore)
        x509Certificate.gmtime_adj_notAfter(notAfter)
    except:
        return 5, None

    x509Certificate.set_issuer(x509CACertificate.get_subject())
    x509Certificate.set_subject(x509Request.get_subject())
    x509Certificate.sign(caPrivateKey, DEFAULT_HASH_FUNCTION)

    return None, OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, x509Certificate)

#Cripto 9.4.0
def pKeyToPEMPrivateKey(keyPair, keyPassphrase, cipher = DEFAULT_CIPHER):
    """
    Taking the given key pair (keyPair), encapsulates its private key on an encrypted PEM
    format, encrypted using cipher algorithm and protected with keyPassphrase passphrase.

    Args:
        keyPair (PKey object): RSA key pair
        keyPassphrase (str): passphrase used to cipher the private key
        cipher (str): cipher algorithm to be used to cipher the private key
    Returns:
        errorCode (int/None), privateKey (PEM/None): If errorCode is None, returns
            private key in PEM format. If errorCode is not None, privateKey will be None.
            The meaning of errorCode is the following:
                1 - invalid key pair or cipher.
    """
    try:
        return None, OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, keyPair, cipher, keyPassphrase)
    except:
        return 1, None

#Cripto 9.5.0
def pKeyToPEMPublicKey(keyPair):
    """
    Extracts the public key from key pair (keyPair) in PEM format.

    Args:
        keyPair (PKey object): RSA key pair
    Returns:
        errorCode (int/None), publicKey (PEM/None): If errorCode is None, returns
            public key in PEM format. If errorCode is not None, publicKey will be None.
            The meaning of errorCode is the following:
                1 - invalid key pair.
    """
    try:
        return None, OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, keyPair)
    except:
        return 1, None

#Cripto 9.6.0
def pemPrivateKeyToPKey(pemPrivateKey, keyPassphrase):
    """
    Transforms the private key in PEM format into the RSA key pair (Pkey object).

    Args:
        pemPrivateKey (PEM): private key in PEM format
        keyPassphrase (str): passphrase used to decipher the private key
    Returns:
        errorCode (int/None), keyPair (PKey object/None): If errorCode is None, returns
            key pair. If errorCode is not None, keyPair will be None.
            The meaning of errorCode is the following:
                1 - invalid private key or passphrase.
    """
    try:
        return None, OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, pemPrivateKey, keyPassphrase)
    except:
        return 1, None
