
import netCDF4
import numpy as np
import os

class File(object):
    def __init__(self, file, xdim, ydim, mode='a', format='NETCDF3_CLASSIC'):
        self.file = file
        if mode != 'w':
            assert os.path.exists(self.file), 'File not existing: ' + self.file
        self.F = netCDF4.Dataset(self.file, mode=mode, format=format)
        self.xdim = xdim
        self.ydim = ydim

    def close(self):
        self.F.close()

    def create_dimension(self, dimname, size):
        self.F.createDimension(dimname, size=size)

    def append_latitude(self, x, vname='latitude'):
        self.append_variable(vname, x)
        self.F.variables[vname].setncattr('long_name', 'latitude')
        self.F.variables[vname].setncattr('units', 'degrees_north')

    def append_longitude(self, x, vname='longitude'):
        self.append_variable(vname, x)
        self.F.variables[vname].setncattr('long_name', 'longitude')
        self.F.variables[vname].setncattr('units', 'degrees_east')

    def append_variable(self, vname, x):
        assert type(x) is np.ma.core.MaskedArray, 'Input needs to be masked array!'
        dummy = -99999.
        assert x.ndim == 2
        self._create_variable(vname, 'd', (self.ydim, self.xdim), fill_value=dummy)

        out = x.data
        out[x.mask] = dummy
        self.F.variables[vname][:,:] = out[:,:]
        try:
            fval = self.F.variables[vname].getncattr('_FillValue')
            print 'Fill value already existing ... will not be set!'
        except:
            self.F.variables[vname].setncattr('_FillValue', dummy)

    def _create_variable(self, vname, dtype, dim, complevel=6, zlib=True, fill_value=None):
        """
        varname : str
            name of variable
        dtype : str
            datatype of variable
        dim : tuple
            tuple specifying the dimensions of the variables
        zlib : bool
            compress outout using zlib
        complevel : int
            compression level
        fill_value : float
            fill value for data
        """
        if vname in self.F.variables.keys():
            print('The variable ' + vname + ' is already existing on the file! SKIPPING')
            return None

        if fill_value is not None:
            self.F.createVariable(vname, dtype, dimensions=dim,
                                  fill_value=fill_value, zlib=zlib, complevel=complevel)
        else:
            self.F.createVariable(
                vname, dtype, dimensions=dim, zlib=zlib, complevel=complevel)

