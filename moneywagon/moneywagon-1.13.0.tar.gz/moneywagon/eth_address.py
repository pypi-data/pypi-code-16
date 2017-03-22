from bitcoin import privtopub
import hashlib
from binascii import unhexlify, hexlify

def secure_privtopub(priv):
    if len(priv) == 64:
        return secure_privtopub(priv.decode('hex')).encode('hex')
    return privtopub(priv)

if not hasattr(hashlib, 'sha3_256'):
    import sha3

def generate_address(seed):
    ethpriv = hashlib.sha3_256(seed).hexdigest()
    return ethpriv, secure_privtopub(ethpriv)[1:]

    sha3 = hashlib.sha3_256(secure_privtopub(ethpriv))
    ethaddr = sha3.hexdigest()[12:] #.encode('hex')
    return ethpriv, ethaddr
