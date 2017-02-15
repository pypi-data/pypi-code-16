import tecplot as tp
from tecplot.constant import *

# Define x/y/z locations of all nodes
nodes0 = ((1,1,5), (2,3,3), (5,1,3), (6,3,2), (3,5,5), (7,5,3), (9,1,5), (10,3,3), (11,5,1))

# Define each cell's node connections (0-based)
conn0 = ((0,1,3,2), (1,4,5,3), (2,3,7,6), (3,5,8,7))

# Define Cell-Centered variable values
scalar_data0 = (33, 55, 22, 64)


# Create the dataset and zones
ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])

# Create FE-Quad zone with 4th variable as Cell Centered
z0 = ds.add_fe_zone(ZoneType.FEQuad,
                    name='Cell Centered Variable',
                    num_points=len(nodes0), num_elements=len(conn0),
                    locations=[ValueLocation.Nodal,ValueLocation.Nodal,ValueLocation.Nodal,ValueLocation.CellCentered]) 

# Fill in and connect first Zone
z0.values('x')[:] = [n[0] for n in nodes0]
z0.values('y')[:] = [n[1] for n in nodes0]
z0.values('z')[:] = [n[2] for n in nodes0]
z0.nodemap[:] = conn0
z0.values('s')[:] = scalar_data0


# Setup a plot and style
plot = tp.active_frame().plot(PlotType.Cartesian3D)
plot.activate()
plot.contour(0).colormap_name = 'Magma'
plot.contour(0).colormap_filter.distribution = tp.constant.ColorMapDistribution.Continuous
plot.show_contour = True

plot.show_mesh = True
plot.view.fit()

# Show Cell Labels at the cell centers for the defined variable
tp.macro.execute_command("""$!GLOBALSCATTER DATALABELS{SHOWCELLLABELS = YES}
                         $!GLOBALSCATTER DATALABELS{CELLLABELTYPE = VARVALUE}
                         $!GLOBALSCATTER DATALABELS{CELLLABELVAR = 4}
                         $!GLOBALTHREED SYMBOLLIFTFRACTION = 8""")

tp.export.save_png('fe_quad_cell_centered.png', 600, supersample=3)

tp.save_layout('test.lpk',include_data=True)