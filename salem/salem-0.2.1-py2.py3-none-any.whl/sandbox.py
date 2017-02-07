import xarray as xr
import salem
from salem import get_demo_file, open_wrf_dataset
import matplotlib.pyplot as plt


f = get_demo_file('wrf_d01_allvars_cropped.nc')
ds = open_wrf_dataset(f)
ds.salem.grid.ll_coordinates

f = get_demo_file('wrfout_d01.nc')
ds = open_wrf_dataset(get_demo_file('wrfout_d01.nc'))

# proj = pday.salem.cartopy()
# ax = plt.axes(projection=proj)
# ax.coastlines(); ax.add_feature(cartopy.feature.BORDERS, linestyle=':');
# ax.set_extent(pday.salem.grid.extent, crs=proj);
# pday.plot(ax=ax)
#
# plt.show()
