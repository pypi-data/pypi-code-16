import hashlib


def sha1(*args: str, encoding='UTF-8', delimiter: bytes = b''):
    """ used to verify message signature"""
    data = []
    for arg in args:
        data.append(arg.encode(encoding))
    data.sort()
    sha = hashlib.sha1()
    sha.update(delimiter.join(data))
    return sha.hexdigest()
