from __future__ import print_function
from __future__ import absolute_import
from asap3 import NeighborCellLocator
from ase.atoms import Atoms
from ase.lattice.cubic import FaceCenteredCubic
import numpy as np
import scipy.spatial
from . import plane_utils
from . import quat_utils
import math


def remove_close(atoms, min_dist):
    "Remove atoms that are too close"
    print("Removing atoms that are too close (d_cut = %.3f Angstrom)" % (min_dist,))
    remove = set()
    nblist = NeighborCellLocator(min_dist, atoms)
    # Loop over all pairs of too-close atoms
    for i in range(len(atoms)):
        for j in nblist[i]:
            # Pair (i,j) is too close
            if not (i in remove or j in remove):
                if len(remove) % 2:
                    remove.add(i)
                else:
                    remove.add(j)
    print("Removing %i atoms out of %i" % (len(remove), len(atoms)))
    del atoms[list(remove)]
    return atoms

def calculate_grain_bounding_planes(centres, size):

    a = (-1, 0, 1)
    ctr = [c for c in centres]
    for i in a:
        for j in a:
            for k in a:
                if i == j == k == 0: continue
                ctr += [size * [i, j, k] + c for c in centres]
    ctr = np.array(ctr)

    voronoi = scipy.spatial.Voronoi(ctr, furthest_site=False, incremental=False, qhull_options=None)
    regions = [voronoi.regions[voronoi.point_region[i]] for i in range(len(centres))]

    grain_cells = []
    for i, reg in enumerate(regions):

        cell_vertices = np.array([voronoi.vertices[v] for v in reg])
        hull = scipy.spatial.ConvexHull(cell_vertices)

        bounding_planes = [plane_utils.plane_equation(centres[i], h, cell_vertices) for h in hull.simplices]
        grain_cells += [(cell_vertices, bounding_planes)]

    return grain_cells


def create_atoms(centres, rotations, unit, size, min_dist):
    "Create the nanocrystalline sample"

    grain_cells = calculate_grain_bounding_planes(centres, size)

    ntotal = 0
    result = None
    for grain_num, (centre, rotation) in enumerate(zip(centres, rotations)):
        assert centre.shape == (3,)
        assert rotation.shape == (3,3)

        (bounding_vertices, bounding_planes) = grain_cells[grain_num]

        #find maximum extent in [x, y, z]
        U = rotation
        rot_basis = U / np.linalg.norm(U, axis=0)

        proj_vertices = np.dot(bounding_vertices, rot_basis)

        xmin = np.min(proj_vertices[:,0])
        ymin = np.min(proj_vertices[:,1])
        zmin = np.min(proj_vertices[:,2])

        xmax = np.max(proj_vertices[:,0])
        ymax = np.max(proj_vertices[:,1])
        zmax = np.max(proj_vertices[:,2])

        #calculate number of unit cells in each direction
        cubic_cell = [unit.cell[0][0], unit.cell[1][1], unit.cell[2][2]]

        x0 = int(math.floor(xmin / cubic_cell[0]))
        y0 = int(math.floor(ymin / cubic_cell[1]))
        z0 = int(math.floor(zmin / cubic_cell[2]))

        x1 = int(math.ceil(xmax / cubic_cell[0]))
        y1 = int(math.ceil(ymax / cubic_cell[1]))
        z1 = int(math.ceil(zmax / cubic_cell[2]))

        #create cube of atoms    #todo: outer product
        positions = [np.dot(U, (np.dot((i, j, k), unit.cell) + atom_pos)) for i in range(x0, x1+1) for j in range(y0, y1+1) for k in range(z0, z1+1) for atom_pos in unit.get_positions()]
        positions = np.array(positions)
        print(len(positions))

        #remove excess atoms
        in_cell = np.ones(len(positions)).astype(np.int8)
        for (p, n) in bounding_planes:
            in_cell = np.logical_and(in_cell, np.dot(n, (positions - p).T) > 0)

        positions = positions[in_cell]

        atoms = Atoms(positions = positions, cell=size, numbers = 29 * np.ones(len(positions)))
        atoms.set_tags(grain_num * np.ones(len(atoms), int))
        if result is None:
            result = atoms
            atoms.set_cell(size, scale_atoms=False)
            atoms.set_pbc(True)
        else:
            result.extend(atoms)
        print("grain: %d contains %d atoms" % (grain_num, len(positions)))

    print("Total atoms:", len(result))
    result = remove_close(result, min_dist)
    print("Remaining atoms:", len(result))
    return result

def make_nanocrystal(size, centres, rotations, min_dist=2.0, unit=None, symbol=None, latticeconstant=None):
    """Create a nanocrystalline sample.

    Parameters:
      size:      Size of the system, in Angstrom (either a number or three numbers).
      centres:   Positions of grains in scaled coordinates.
      rotations: Rotation matrices for the grains.

      min_dist (optional):
                 If two atoms are closer than this distance, one of them is removed
                 (default: 2.0).

    In addition, either the 'unit' or the 'symbol' parameter must be specified.
      unit (optional):
                 A unit cell for building the crystals (Atoms object).
                 MUST be orthorhombic!
      symbol (optional):
                 If unit is None, then an FCC crystal of this element is used.
      latticeconstant (optional):
                 If symbol is specified, this overrides the default lattice constant.
    """

    assert type(size) == float or type(size) == list
    if type(size) == float:
        size = np.array([size, size, size])
    elif type(size) == list:
        size = np.array(size)
    assert size.shape == (3,)
    assert len(centres) == len(rotations)
    centres *= size
    if unit is None:
        unit = FaceCenteredCubic(symbol=symbol, size=(1,1,1), pbc=True, latticeconstant=latticeconstant)

    return create_atoms(centres, rotations, unit, size, min_dist)

