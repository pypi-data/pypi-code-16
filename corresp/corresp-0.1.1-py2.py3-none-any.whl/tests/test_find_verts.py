import unittest
#from chainer_uc.visualizations.vis_dense_correspondence import find_verts
from corresp.find_verts import find_verts
import numpy as np


class TestVizDense(unittest.TestCase):

    def test_verts(self):
        # test in the cease when src and dest are same
        H = 5
        W = 5
        C = 3
        src_feat = np.arange(C * H * W).reshape(C, H, W).astype(np.float32)
        dest_feat = src_feat.copy().astype(np.float32)
        
        vert_pairs = find_verts(src_feat, dest_feat, gpu=0)

        for i in range(H):
            for j in range(W):
                np.testing.assert_equal(vert_pairs[0, i * j], vert_pairs[1, i * j])



if __name__ == '__main__':
    unittest.main()
