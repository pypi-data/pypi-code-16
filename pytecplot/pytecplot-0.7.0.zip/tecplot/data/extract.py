from ..tecutil import _tecutil
from .. import layout
from ..constant import *
from ..exception import TecplotSystemError, TecplotLogicError
from ..tecutil import ArgList, lock, sv


@lock()
def extract_slice(origin=(0, 0, 0), normal=(0, 0, 1), **kwargs):
    frame, dataset, kwargs = layout.util.kwargs_pop_dataset(**kwargs)

    if __debug__:
        if frame.plot_type is not PlotType.Cartesian3D:
            msg = 'Plot Type must be Cartesian3D to create a slice.'
            raise TecplotLogicError(msg)

    with frame.activated():
        new_zone_index = dataset.num_zones
        with ArgList() as arglist:
            arglist[sv.ORIGINX] = float(origin[0])
            arglist[sv.ORIGINY] = float(origin[1])
            arglist[sv.ORIGINZ] = float(origin[2])
            arglist[sv.NORMALX] = float(normal[0])
            arglist[sv.NORMALY] = float(normal[1])
            arglist[sv.NORMALZ] = float(normal[2])
            for k, v in kwargs.items():
                arglist[k.upper()] = v
            if not _tecutil.CreateSliceZoneFromPlneX(arglist):
                raise TecplotSystemError()
            if dataset.num_zones == new_zone_index:
                raise TecplotLogicError('No zones found when extracting slice')
            return dataset.zone(new_zone_index)
