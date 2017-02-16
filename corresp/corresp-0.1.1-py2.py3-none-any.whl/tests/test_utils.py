import unittest

import numpy as np

from corresp.utils import rescale_verts


class TestRescaleVerts(unittest.TestCase):

    def test_rescale_verts(self):
        out_H = 376
        out_W = 1242
        in_H = 94
        in_W = 310
        
        # create verts
        n_verts = 100
        v_coords = np.random.choice(in_H, size=(2, n_verts, 1))
        u_coords = np.random.choice(in_W, size=(2, n_verts, 1))
        verts = np.concatenate((v_coords, u_coords), axis=2)

        out_verts = rescale_verts(verts, in_H, in_W, out_H, out_W)

        # TODO: evaluation
