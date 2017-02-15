from ..tecutil import _tecutil, flatten_args, IndexSet
from ..tecutil import lock
from ..exception import TecplotSystemError


@lock()
def interpolate_linear(dest_zone, *src_zones):
    """Linear interpolater"""
    src_zones = flatten_args(*src_zones)
    with IndexSet(*src_zones) as src:
        dest = dest_zone.index+1
        if not _tecutil.LinearInterpolate(src, dest, None, 0., 0):
            raise TecplotSystemError()
