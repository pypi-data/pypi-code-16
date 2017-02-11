__doc__ = '''gpio3 is a comfy yet reasonably efficient GPIO interface for python.

Example usage for the impatient:

    >>> import gpio3
    >>> 
    >>> g = gpio3.LinuxGPIO(203)
    >>> # or gpio3.LinuxGPIO(gpio3.mainline_sunxi_pin("PG11"))
    >>> g.direction
    'in'
    >>> g.value
    0
    >>> g.direction = 'out'
    >>> g.direction
    'out'
    >>> g.value
    0
    >>> g.value = 1
    >>> g.value
    1
'''

from .gpio import BaseGPIO, LinuxGPIO
from .util import mainline_sunxi_pin
