from operator import xor
import hmac
import hashlib
import base64


def pad(key, plaintext, hmac_key=None):
    '''
    Performs a one time pad on two strings.
    :params - plaintext: plaintext and key are strings of equal length
            - key: plaintext and key are strings of equal length
            - hmac_key: if a key is present, will add key 'digest' to return dictionary
    :returns - dictionary with key 'encrypted' which is the resultant from the XOR as a string.
               If :param hmac_key is present, will also have key 'digest' in return dictionary
    '''
    assert len(plaintext) == len(key)
    plaintext_bytes, key_bytes = bytearray(plaintext), bytearray(key)
    padded = bytearray([1] * len(key_bytes))

    for i, _ in enumerate(key_bytes):
        padded[i] = xor(plaintext_bytes[i], key_bytes[i])
    b64_padded = base64.b64encode(padded)

    if not hmac_key:
        return {'encrypted': b64_padded}

    digest = hmac.new(hmac_key, msg=b64_padded, digestmod=hashlib.sha256).digest()
    digest = base64.b64encode(digest)
    return {'encrypted': b64_padded, 'digest': digest}


def unpad(key, encrypted_text, hmac_key=None, hmac_digest=None):
    '''
    Performs a one time pad on two strings and optionally verifies the hmac.
    :params - key: key and encrypted_key are strings of equal length
            - encrypted_key: key and encrypted_key are strings of equal length
            - hmac_key: if a key is present, will verify and throw exception if not valid
    :returns - dictionary with key 'decrypted' which is the resultant from the XOR as a string.
    '''
    raw_encrypted_text = base64.b64decode(encrypted_text)
    assert len(key) == len(raw_encrypted_text)

    if hmac_key:
        if not hmac_digest:
            raise Exception('hmac_key with no hmac_digest')
        digest = hmac.new(hmac_key, msg=encrypted_text, digestmod=hashlib.sha256).digest()
        digest = base64.b64encode(digest)
        if _safe_string_compare(digest, hmac_digest) is False:
            raise Exception('computed hmac of encrypted_text does not match the hmac_digest')

    key_bytes, encrypted_bytes = bytearray(key), bytearray(raw_encrypted_text)
    padded = bytearray([1] * len(key_bytes))

    for i, _ in enumerate(key_bytes):
        padded[i] = xor(key_bytes[i], encrypted_bytes[i])
    padded = str(padded.decode('utf-8'))
    return {'decrypted': padded}


def _safe_string_compare(string1, string2):
    if len(string1) != len(string2):
        return False
    result = 0
    for x, y in zip(string1, string2):
        result |= ord(x) ^ ord(y)
    return result == 0
