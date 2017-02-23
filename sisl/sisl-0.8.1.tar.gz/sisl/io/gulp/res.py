"""
Sile object for reading/writing GULP in/output
"""
from __future__ import print_function, division

# Import sile objects
from .hessian import HessianSileGULP
from .sile import SileGULP
from ..sile import *

# Import the geometry object
from sisl import Geometry, Atom, SuperCell
from sisl.quantity import DynamicalMatrix

import numpy as np

__all__ = ['resSileGULP']


class resSileGULP(SileGULP):
    """ GULP output file object """

    @Sile_fh_open
    def read_sc(self, *args, **kwargs):
        """ Reads a `SuperCell` and creates the GULP cell """

        f, _ = self.step_to('cell')
        if not f:
            raise ValueError(
                ('GULPSile tries to lookup the SuperCell vectors. '
                 'This could not be found found in file: "' + self.file + '".'))

        cell = [float(x) for x in self.readline().split()]

        return SuperCell(cell)

    @Sile_fh_open
    def read_geom(self, *args, **kwargs):
        """ Reads a geometry and creates the GULP dynamical geometry """

        sc = self.read_sc(*args, **kwargs)

        f, _ = self.step_to('fractional')

        atom = []
        xyz = []
        line = self.readline().split()
        while len(line) >= 5:
            # Keep reading the atoms (each atom has 3 "orbitals")
            atom.append(Atom(line[0], orbs=3))
            xyz.append([float(x) for x in line[2:5]])
            line = self.readline().split()

        xyz = np.array(xyz)
        # It is fractional
        xyz = np.dot(xyz, sc.cell)

        # jump to supercell
        f, line = self.step_to('ghost_supercell')
        if not f:
            raise ValueError("Could not find 'ghost_supercell' in the res-file")
        g_sc = [int(x) for x in line.split()[1:]]

        # Create geom
        geom = Geometry(xyz, atom, sc=sc)

        # Reduce the geometry according to the supercell
        # GULP does:
        # do x
        #  do y
        #   do z
        #   end do
        #  end do
        # end do
        sc = sc.cut(g_sc[2], 2).cut(g_cs[1], 1).cut(g_cs[0], 0)
        # select the atoms that we should keep
        idx =     np.arange(0, len(geom), g_sc[2])
        idx = idx[np.arange(0, len(idx), g_sc[1]))
        idx = idx[np.arange(0, len(idx), g_sc[0]))

        return geom.sub(idx, cell=sc)

    def read_dynmat(self, *args, **kwargs):
        """ Reads the dynamical matrix from the accompanying FORCE_CONSTANTS_2ND file

        This will automatically reduce the sparse matrix
        to the correct ghost-cell
        """
        # We will use this extensively
        from numpy import array

        # Read number of supercells
        with self:
            f, line = self.step_to('ghost_supercell')
        if not f:
            raise ValueError("Could not find 'ghost_supercell' in the res-file")
        g_sc = array([int(x) for x in line.split()[1:]])

        # Extract the required size, if requested
        nsc = kwargs.pop('nsc', None)
        if nsc is None:
            # we default to half the ghost_supercell
            nsc = (g_sc // 2) * 2 + 1

        # Read the geometry, and read the
        geom = self.read_geom()
        # Update the number of super-cells stored
        geom.set_nsc(nsc)
        na = len(geom)
        # size of orbital setup
        no = geom.no
        dyn_big = HessianSileGULP('FORCE_CONSTANTS_2ND').read_dynmat(*args, **kwargs)

        # Now, we should reduce...
        # Easier for creation of the sparsity pattern
        from scipy.sparse import lil_matrix

        # Create the complete sparse matrix
        dyn = lil_matrix((geom.no, geom.no_s), dtype=dtype)

        # Convert the matrix
        # This is slightly more complicated than
        # the traditional setup as we need to construct
        # the symmetric couplings
        from itertools import product
        ib = 0
        jb = 0
        for ia, ja in product(range(na), range(na)):
            # Transfer to the initial "orbital"
            io = ia * 3
            jo = ja * 3
            # Now loop the expansions
            for ix, iy, iz in product(*map(range, g_sc))):
                sc_off = array([ix, iy, iz], np.int32)
                ioff = geom.sc_index(sc_off) * no

                dyn[io, ioff + jo] = dyn_big[io, jb]
                dyn[io, ioff + jo+1] = dyn_big[io, jb+1]
                dyn[io, ioff + jo+2] = dyn_big[io, jb+2]
                dyn[io+1, ioff + jo] = dyn_big[io+1, jb]
                dyn[io+1, ioff + jo+1] = dyn_big[io+1, jb+1]
                dyn[io+1, ioff + jo+2] = dyn_big[io+1, jb+2]
                dyn[io+2, ioff + jo] = dyn_big[io+2, jb]
                dyn[io+2, ioff + jo+1] = dyn_big[io+2, jb+1]
                dyn[io+2, ioff + jo+2] = dyn_big[io+2, jb+2]

                # If this is not the unit-cell, then
                # also create the mirror
                if ix != 0 or iy != 0 or iz != 0:
                    ioff = geom.sc_index(-sc_off) * no
                    dyn[jo, ioff + io] = dyn_big[jb, ib]
                    dyn[jo, ioff + io+1] = dyn_big[jb, ib+1]
                    dyn[jo, ioff + io+2] = dyn_big[jb, ib+2]
                    dyn[jo+1, ioff + io] = dyn_big[jb+1, ib]
                    dyn[jo+1, ioff + io+1] = dyn_big[jb+1, ib+1]
                    dyn[jo+1, ioff + io+2] = dyn_big[jb+1, ib+2]
                    dyn[jo+2, ioff + io] = dyn_big[jb+2, ib]
                    dyn[jo+2, ioff + io+1] = dyn_big[jb+2, ib+1]
                    dyn[jo+2, ioff + io+2] = dyn_big[jb+2, ib+2]

                jb += 3
            if ja == na - 1:
                ib += 3






add_sile('res', resSileGULP, gzip=True)
