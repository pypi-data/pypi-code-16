import tecplot as tp
from tecplot.constant import *

# Zone 0

# Define x/y/z locations of all nodes
nodes0 = ((1,1,5), (2,3,3), (5,1,3), (6,3,2), (3,5,5), (7,5,3))

# Create Cell-Centered variable 
scalar_data0 = (33, 55)

# Define each cell nodal connections (0-based)
conn0 = ((0,1,3,2),(1,4,5,3))

# Define cell faces which are shared (position) and which cell in the neighboring zone (0-based value)
neighbors0 = ((None, None, 0, None), (None, None, 1, None))

# Define the zone which the cell face is neighboring (0-based value)
neighbor_zones0 = ((None, None, 1, None), (None, None, 0, None))

# Repeate same properties for Zone 1
nodes1 = ((5,1,3), (9,1,5), (6,3,2), (10,3,3), (7,5,3), (11,5,5))
scalar_data1 = (22, 64)
conn1 = ((0,2,3,1),(2,4,5,3))
neighbors1 = ((0, None, None, None), (1, None, None, None))
neighbor_zones1 = ((0, None, None, None), (0, None, None, None))

# Create the dataset and zones
ds = tp.active_frame().create_dataset('Data', ['x','y','z'])#,'s'])
z0 = ds.add_fe_zone(ZoneType.FEQuad,
                    name='Left Side',
                    num_points=len(nodes0), num_elements=len(conn0),
                    face_neighbor_mode=FaceNeighborMode.GlobalOneToOne) # Working with face maps between zones (Global) and a single face has only one neigbhor

z1 = ds.add_fe_zone(ZoneType.FEQuad,
                    name='Right Side',
                    num_points=len(nodes1), num_elements=len(conn1),
                    face_neighbor_mode=FaceNeighborMode.GlobalOneToOne)


# Fill in and connect first Zone
z0.values('x')[:] = [n[0] for n in nodes0]
z0.values('y')[:] = [n[1] for n in nodes0]
z0.values('z')[:] = [n[2] for n in nodes0]
z0.nodemap[:] = conn0


# Fill in and connect second Zone
z1.values('x')[:] = [n[0] for n in nodes1]
z1.values('y')[:] = [n[1] for n in nodes1]
z1.values('z')[:] = [n[2] for n in nodes1]
z1.nodemap[:] = conn1


# Setup a plot and style
plot = tp.active_frame().plot(PlotType.Cartesian3D)
plot.activate()

plot.show_edge = True

# Turning on mesh, we can see the two zones having continous shading
plot.show_mesh = True
plot.fieldmap(0).mesh.color = tp.constant.Color.Red # Color first zone red
plot.fieldmap(1).mesh.color = tp.constant.Color.WarmBlue # Color first zone red

for fmap in plot.fieldmaps:
    fmap.mesh.line_pattern = LinePattern.Dashed
    fmap.mesh.line_thickness = .8
    fmap.edge.line_thickness = .8

for ax in plot.axes:
    ax.show = True
plot.axes.grid_area.fill_color = tp.constant.Color.Grey
    
plot.view.alpha = 5
plot.view.psi = 50
plot.view.theta = -120
plot.view.fit()

tp.export.save_png('fe_quad_sans_neighbors.png', 600, supersample=3)

# Set face neighbors
z0.face_neighbors.set_neighbors(neighbors0, neighbor_zones0, obscures=True)
z1.face_neighbors.set_neighbors(neighbors1, neighbor_zones1, obscures=True)

tp.export.save_png('fe_quad_neighbored.png', 600, supersample=3)

tp.save_layout('test.lpk',include_data=True)