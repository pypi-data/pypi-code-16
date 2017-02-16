import numpy as np


def verts2flow(verts, H, W):
    """Convert vertices representation to flow representation.
    Args:
        verts (2, n_verts, 2)

    Returns:
        flow (H, W, 3)
    """
    flow = np.zeros((H, W, 3))
    
    _, n_verts, _ = verts.shape

    for i in range(n_verts):
        src = verts[0, i]
        dst = verts[1, i]

        flow[src[0], src[1], 0] = dst[0] - src[0]
        flow[src[0], src[1], 1] = dst[1] - src[1]
        flow[src[0], src[1], 2] = 1
    return flow
