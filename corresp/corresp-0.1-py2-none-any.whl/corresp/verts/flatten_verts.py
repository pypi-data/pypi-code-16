import numpy as np


def flatten_verts(verts, shape):
    """
    Args:
        verts (n_verts, 2)
    Returns:
        (n_verts, )
    """
    assert verts.ndim == 2 and verts.shape[1] == 2
    ravel_index = np.ravel_multi_index(verts.T, shape)
    return ravel_index
