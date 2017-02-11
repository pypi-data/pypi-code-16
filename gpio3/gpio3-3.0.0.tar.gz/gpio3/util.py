import re

_mainline_sunxi_pin_re = re.compile(r"P([A-Z])(\d+)")
def mainline_sunxi_pin(name):
    '''Resolve pin name (e.g. "PG11") to pin index on allwinner devices on mainline kernels.

Note: I've only tested this on a Cubieboard1.
'''
    m = _mainline_sunxi_pin_re.fullmatch(name)
    if m is None:
        raise ValueError("unrecognized pin name {!r}".format(name))
    i, j = ord(m.group(1))-ord('A'), int(m.group(2))
    return 32*i+j

