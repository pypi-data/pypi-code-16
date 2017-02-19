
def traditional(size):
    try:
        size = int(size)
    except:
        raise ValueError("filesize requires a numeric value, not {!r}".format(size))
    suffixes = ('kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    base = 1024
    if size == 1:
        return '1 byte'
    elif size < base:
        return '{:,} bytes'.format(size)

    for i, suffix in enumerate(suffixes):
        unit = base ** (i + 2)
        if size < unit:
            return "{:,.01f} {}".format((base * size / unit), suffix)
    return "{:,.01f} {}".format((base * size / unit), suffix)
