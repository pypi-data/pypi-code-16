# coding: latin-1

###############################################################################
# eVotUM - Electronic Voting System
#
# pkiutils.py
#
# Cripto-5.0.0 - Public Key cryptography Functions
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
Public-key cryptography, or asymmetric cryptography, is an encryption scheme that
uses two mathematically related, but not identical, keys - a public key and a private key.

It is computationally infeasible to compute the private key based on the public key.
Because of this, public keys can be freely shared, allowing users an easy and convenient
method for encrypting content and verifying digital signatures, and private keys
must be kept secret, ensuring only the owners of the private keys can decrypt content
and create digital signatures.

Since public keys need to be shared but are too big to be easily remembered, they are
stored on digital certificates for secure transport and sharing. Since private keys are
not shared, they are simply stored in the software or operating system you use, or on
hardware (e.g., USB token, hardware security module) containing drivers that allow it
to be used with your software or operating system.

Digital certificates are issued by entities known as Certificate Authorities (CAs).

Two of the best-known uses of public-key cryptography are:
  + Digital signatures - content is digitally signed with an individual’s private
  key and is verified by the individual’s public key;
  + Encryption - content is encrypted using an individual’s public key and can only
  be decrypted with the individual’s private key.

Digital signatures offers the following security benefits:
  + Authentication – since the individual’s unique private key was used to apply
  the signature, recipients can be confident that the individual was the one to
  actually apply the signature;
  + Non-repudiation – since the individual is the only one with access to the private
  key used to apply the signature, he/she cannot later claim that it wasn’t him/her
  who applied the signature;
  + Integrity - when the signature is verified, it checks that the contents of the
  document or message match what was in there when the signature was applied. Even
  the slightest change to the original document would cause this check to fail.

Encryption offers the following security benefits:
  + Confidentiality - because the content is encrypted with an individual’s public key,
  it can only be decrypted with the individual’s private key, ensuring only the intended
  recipient can decrypt and view the contents;
  + Integrity - part of the decryption process involves verifying that the contents of
  the original encrypted message and the new decrypted match, so even the slightest change
  to the original content would cause the decryption process to fail.
"""

from eVotUM.Cripto import utils

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.Cipher import AES

import OpenSSL, jose, base64

AES_KEY_BYTES_LENGTH = 32
ENC_OBJECT_LENGTH = 3

#Cripto 5.1.0
def getPublicKeyFromCertificate(pemCertificate):
    """
    Retrieves public key from digital certificate in PEM format.
    Args:
        pemCertificate (pem): digital certificate in PEM format
    Returns:
        errorCode (int/None), publicKey (pem/None): tuple with error code and public key in
            PEM format.
            The errorCode has the following meaning:
                None - the public key was retrieved and the certificate was within the validity period
                1 - the public key was retrieved but the certificate is not within the validity period
                2 - the certificate format is invalid (not PEM)
                3 - it was not possible to retrieve the public key from the certificate
            If the errorCode is 2 or 3, publicKey will be None
    """
    try:
        x509Certificate = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, pemCertificate)
        if (x509Certificate is not None):
            expiredCertificate = x509Certificate.has_expired()
        else:
            return 2, None
    except:
        return 2, None

    try:
        publicKey = x509Certificate.get_pubkey()
        pemPublicKey = OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, publicKey)
        if (not expiredCertificate):
            return None, pemPublicKey
        else:
            return 1, pemPublicKey
    except:
        return 3, None

#Cripto 5.2.0
def encryptWithPublicKey(plaintext, pemCertificate):
    """
    Encrypts plaintext with the public key in pemCertificate (digital certificate in PEM format).
    Note: This function doesn't validate if pemCertificate is a well formed digital certificate
    in PEM format. Please use other functions to validate.
    Args:
        plaintext (str): string to be ciphered
        pemCertificate (pem): digital certificate in PEM format
    Returns:
        encObject (base64/None): return the encrypted payload. If it is not possible
        to retrieve the public key form pemCertificate, the return value will be None
    """
    errorCode, pemPublicKey = getPublicKeyFromCertificate(pemCertificate)

    if (pemPublicKey):
        key = utils.generateRandomData(AES_KEY_BYTES_LENGTH)
        iv = utils.generateRandomData(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pkcs5Pad(plaintext, AES.block_size))

        publicKey = RSA.importKey(pemPublicKey)
        publicKeyOAEP = PKCS1_OAEP.new(publicKey, hashAlgo=SHA256)
        encryptedKey = publicKeyOAEP.encrypt(key)

        encObjectStr = "%s,%s,%s" % (base64.b64encode(encryptedKey), iv.encode("hex"), base64.b64encode(ciphertext))
        return base64.b64encode(encObjectStr)

    return None

#Cripto 5.3.0
def verifyCertificateChain(pemCertificate, rootPEMCertificate):
    """
    Verify if pemCertificate (digital certificate in PEM format) has been signed by
    rootPEMCertificate (Certification Authority digital certificate in PEM format).
    Note: This function doesn't validate if pemCertificate or rootPEMCertificate are
    well formed digital certificates in PEM format. Please use other functions to validate.
    Args:
        pemCertificate (pem): digital certificate in PEM format
        rootPEMCertificate (pem): Certification Authority digital certificate in PEM format
    Returns:
        boolean: True if pemCertificate was signed by rootPEMCertificate; False otherwise.
    """
    rootX509Certificate = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, rootPEMCertificate)
    x509Certificate = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, pemCertificate)

    x509Store = OpenSSL.crypto.X509Store()
    x509Store.add_cert(rootX509Certificate)
    storeContext = OpenSSL.crypto.X509StoreContext(x509Store, x509Certificate)

    try:
        storeContext.verify_certificate()
        return True
    except:
        return False

#Cripto 5.4.0
def decryptWithPrivateKey(encObject, pemPrivateKey, keyPassphrase):
    """
    Deciphers b64Ciphertext with pemPrivateKey (private key in PEM format), using
    keyPassphrase to access the pemPrivateKey.
    Note: This function doesn't validate if privateKey is a well formed private key
    in PEM format. Please use other functions to validate.
    Args:
        encObject (base64): encrypted payload
        pemPrivateKey (pem): private key in PEM format
        keyPassphrase (str): passphrase to access pemPrivateKey
    Returns:
        errorCode (int/None), plaintext (str/None): tuple with error code and deciphered b64Ciphertext.
            The errorCode has the following meaning:
                None - b64Ciphertext was deciphered with success
                1 - symmetric key could not be deciphered
                2 - one or more encrypted object compoenents could not be decoded
                3 - ciphertext could not be deciphered
            If the errorCode is not None, plaintext will be None
    """
    try:
        encObjectStr = base64.b64decode(encObject).split(",")
        encryptedKey = base64.b64decode(encObjectStr[0])
        iv = encObjectStr[1].decode("hex")
        ciphertext = base64.b64decode(encObjectStr[2])
    except:
        return 2, None

    privateKey = RSA.importKey(pemPrivateKey, keyPassphrase)
    privateKeyOAEP = PKCS1_OAEP.new(privateKey, hashAlgo=SHA256)

    try:
        key = privateKeyOAEP.decrypt(encryptedKey)
    except:
        return 1, None

    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = pkcs5Unpad(cipher.decrypt(ciphertext))
        return None, plaintext
    except:
        return 3, None

#Cripto 5.5.0
def verifyPEMCertificate(pemCertificate):
    """
    Verify if pemCertificate (digital certificate) is a well formed digital certificate
    in PEM format.
    Args:
        pemCertificate (pem): digital certificate
    Returns:
        boolean: True if pemCertificate is well formed (PEM format); False otherwise.
    """
    try:
        x509Certificate = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, pemCertificate)
        return True
    except:
        return False

#Cripto 5.6.0
def verifyPEMPrivateKey(pemPrivateKey, keyPassphrase=None):
    """
    Verify if pemPrivateKey (private key) is a well formed private key in PEM format,
    using keyPassphrase to access the pemPrivateKey.
    Args:
        pemPrivateKey (pem): private key
    Returns:
        boolean: True if pemPrivateKey is well formed (PEM format); False otherwise.
    """
    try:
        OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, pemPrivateKey, keyPassphrase)
        return True
    except:
        return False

#Cripto 5.12.0
def signObject(object, pemPrivateKey, keyPassphrase):
    """
    Signs object with pemPrivateKey (private key) - keyPassphrase to access pemPrivateKey -.
    Note: This function doesn't validate if privateKey is a well formed private key
    in PEM format. Please use other functions to validate.
    Args:
        object (str): object to sign
        pemPrivateKey (pem): private key in PEM format
        keyPassphrase (str): passphrase to access pemPrivateKey
    Returns:
        errorCode (int/None), JWT (base64): tuple with error code and JSON Web Signature (JWS).
            The errorCode has the following meaning:
                None - JWS was created with success
                1 - JWS could not be created
            If the errorCode is 1, JWT will be None
    """
    jwkPrivateKey = {"k": pemPrivateKey, "passphrase": keyPassphrase}
    toSign = {"object": object}

    try:
        joseJWS = jose.sign(toSign, jwkPrivateKey, alg="RS256")
        return None, jose.serialize_compact(joseJWS)
    except:
        return 1, None

#Cripto 5.13.0
def verifyObjectSignature(jwtSignature, pemCertificate):
    """
    Verifies that jwtSignature (JSON Web Signature) is well formated and was signed
    with the private key associated to the public key in the digital certificate
    pemCertificate. Returns the signed object (contained in jwtSignature).
    Args:
        jwtSignature (base64): JSON Web Signature (JWS)
        pemCertificate (pem): digital certificate in PEM format
    Returns:
        errorCode (int/None), object (str/None): tuple with error code and object.
            The errorCode has the following meaning:
                None - jwtSignature is well formated and was signed with the private
                    key associated to the public key in pemCertificate
                1 - jwtSignature is well formated and was signed with the private
                    key associated to the public key in pemCertificate, but the
                    certificate is not within the validity period
                2 - pemCertificate format is invalid (not PEM)
                3 - it was not possible to retrieve the public key from pemCertificate
                4 - jwtSignature is not well formated or was not signed with the private
                    key associated to the public key in pemCertificate
            If the errorCode is 2, 3 or 4, object will be None
    """
    object = None
    errorCode, pemPublicKey = getPublicKeyFromCertificate(pemCertificate)
    jwkPublicKey = {"k": pemPublicKey}

    if (errorCode < 2):
        try:
            verificationResult = jose.verify(jose.deserialize_compact(jwtSignature), jwkPublicKey, alg="RS256")
            object = verificationResult[1]["object"]
        except:
            errorCode = 4

    return errorCode, object

#utils
def pkcs5Pad(data, blockSize):
    return data + (blockSize - len(data) % blockSize) * chr(blockSize - len(data) % blockSize)

def pkcs5Unpad(data):
    return data[0:-ord(data[-1])]
