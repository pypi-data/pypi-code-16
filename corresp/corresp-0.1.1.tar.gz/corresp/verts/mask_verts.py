import numpy as np


def mask_verts(verts, mask, H, W):
    """
    Args:
        obtained (2, n_verts, 2)
        mask (n, 2):  coordinates of vertices in source image that
            you are intereseted in.
    """
    assert np.max(verts[:, :, 0]) < H
    assert np.max(verts[:, :, 1]) < W

    verts = verts.reshape(2, H, W, 2)
    selected = verts[:, mask[:, 0], mask[:, 1], :]
    return selected
