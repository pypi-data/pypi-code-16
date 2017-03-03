from functools import wraps

def lookup(data, path, default=0xDEADBEEF):
    if not isinstance(data, dict):
        raise ValueError("lookup context must be a dictionary, got %r: %r" % (type(data), data))
    if not isinstance(path, str):
        raise ValueError("path must be a string, given %r", path)
    try:
        bits = path.split('.', 1)
        if len(bits) > 1:
            bit, rest = bits
        else:
            bit, rest = bits[0], []
        val = data[bit]
        if rest:
            return lookup(val, rest, default)
        return val
    except KeyError:
        if default == 0xDEADBEEF:
            raise
        return default

def path(p, default=0xDEADBEEF):
    def fn(data):
        if p == None:
            return data
        return lookup(data, p, default)
    fn.__name__ = 'path'
    return fn

def val(v):
    "simple placeholder for the value coming from the list of items"
    return v
