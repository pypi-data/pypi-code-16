import numpy as np
import os
import sys

np.seterr('raise')

if "--old" not in sys.argv:
    sys.path.insert(0, "/root/python/yt-kdtree/")
    plotfile = "kdtree.png"
else:
    sys.path.insert(
        0, "/root/anaconda/pkgs/yt-3.2.3-py27_0/lib/python2.7/site-packages/")
    plotfile = "clean.png"

import yt
print("Using yt installed in {}".format(os.path.dirname(yt.__file__)))

fname = "/mnt/gv0/yt_data/GadgetDiskGalaxy/snapshot_200.hdf5"
# fname = "/mnt/gv0/yt_data/snapshot_033/snap_033.0.hdf5"
ds = yt.load(fname)
# print((ds.r[:]["gas", "density"] == 0.0).sum()
#         / float(ds.r[:]["gas", "density"].size))

p = yt.ProjectionPlot(ds, "x", ("gas", "density"))
p.zoom(10)
p.save(plotfile)
