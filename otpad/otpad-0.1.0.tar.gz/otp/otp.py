from operator import xor


def onetimepad(key1, key2):
    '''
    Performs a one time pad on two strings.
    :params - key1: key 1 and key 2 are strings of equal length
            - key2: key 1 and key 2 are strings of equal length
    :returns - the resultant from the XOR as a string
    Note: key1 and key2 must be the same length
          and that operations are symmetric
    '''
    assert len(key1) == len(key2)
    key1_bytes, key2_bytes = bytearray(key1), bytearray(key2)
    padded = bytearray([1] * len(key1_bytes))

    for i, _ in enumerate(key1_bytes):
        padded[i] = xor(key1_bytes[i], key2_bytes[i])
    padded = padded.decode('utf-8')
    return str(padded)
