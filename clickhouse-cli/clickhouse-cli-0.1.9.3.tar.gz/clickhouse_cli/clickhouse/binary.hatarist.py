def varint_length(x):
    return sum(x >= r for r in (0, 1 << 7, 1 << 14, 1 << 21, 1 << 28, 1 << 35, 1 << 42, 1 << 49, 1 << 56))


def varint2int(x):
    result = 0

    for i, b in enumerate(x):
        result = result | (ord(b) & 0x7f) << (7 * i)

        if not (ord(b) & 0x80):
            return result
