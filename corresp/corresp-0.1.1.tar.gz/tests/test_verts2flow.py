import unittest

import numpy as np

from corresp.verts2flow import verts2flow


class TestVerts2Flow(unittest.TestCase):

    def test_verts2flow(self):
        H = 100
        W = 150
        n_verts = 100

        v_coords = np.random.choice(H, size=(2, n_verts, 1))
        u_coords = np.random.choice(W, size=(2, n_verts, 1))
        verts = np.concatenate((v_coords, u_coords), axis=2)

        img = verts2flow(verts, H, W)

        for i in range(n_verts):
            src = verts[0, i]
            dst = verts[1, i]

            assert img[src[0], src[1], 0] == dst[0] - src[0]
            assert img[src[0], src[1], 1] == dst[1] - src[1]
            assert img[src[0], src[1], 2] == 1
