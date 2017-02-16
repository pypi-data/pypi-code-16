import numpy as np
from sklearn.neighbors import NearestNeighbors


def find_verts(src_feat, dest_feat, gpu=-1):
    """
    Args:
        # watch out for dimensions
        src_feat (C, H, W)
        dest_feat (C, H, W) 

    Returns:
        vert_pairs (2, H*W, 2)
    """

    C, H, W = src_feat.shape
    # print 'C={}  H={}  W={}'.format(C, H, W)
    src_feat = np.transpose(src_feat, axes=(1, 2, 0)).reshape(H*W, C)
    dest_feat = np.transpose(dest_feat, axes=(1, 2, 0)).reshape(H*W, C)

    if gpu == -1:
        nbrs = NearestNeighbors(n_neighbors=1, n_jobs=6).fit(dest_feat)
        indices = nbrs.kneighbors(src_feat, return_distance=False).ravel()
    else:
        import nn_gpu
        indices = nn_gpu.nn(src_feat, dest_feat)
        indices = indices

    indices = np.unravel_index(indices, (H, W))
    dest_verts = np.stack(indices, axis=1)

    src_verts = np.stack(np.unravel_index(np.arange(H*W), (H, W)), axis=1)

    vert_pairs = np.stack([src_verts, dest_verts], axis=0)
    return vert_pairs
