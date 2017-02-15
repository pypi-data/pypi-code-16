import os
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

import tecplot

examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, 'OneraM6wing', 'OneraM6_SU2_RANS.plt')
dataset = tecplot.data.load_tecplot(datafile)

frame = tecplot.active_frame()
frame.plot_type = tecplot.constant.PlotType.Cartesian3D
frame.plot().show_contour = True

# export image of wing
tecplot.export.save_png('wing.png', 600)

# extract an arbitrary slice from the surface data on the wing
extracted_slice = tecplot.data.extract.extract_slice(
    origin=(0, 0.25, 0),
    normal=(0, 1, 0),
    slicesource=tecplot.constant.SliceSource.SurfaceZones,
    dataset=dataset)

extracted_slice.name = 'Quarter-chord C_p'

# get x from slice
extracted_x = extracted_slice.values('x')

# copy of data as a numpy array
x = extracted_x.as_numpy_array()

# normalize x
xc = (x - x.min()) / (x.max() - x.min())
extracted_x[:] = xc

# switch plot type in current frame
frame.plot_type = tecplot.constant.PlotType.XYLine
plot = frame.plot()

# clear plot
plot.delete_linemaps()

# create line plot from extracted zone data
cp_linemap = plot.add_linemap(
    name=extracted_slice.name,
    zone=extracted_slice,
    x=dataset.variable('x'),
    y=dataset.variable('Pressure_Coefficient'))

# set style of linemap plot
cp_linemap.line.color = tecplot.constant.Color.Blue
cp_linemap.line.line_thickness = 0.8
cp_linemap.y_axis.reverse = True

# update axes limits to show data
plot.view.fit()

# export image of pressure coefficient as a function of x/c
tecplot.export.save_png('wing_pressure_coefficient.png', 600)
