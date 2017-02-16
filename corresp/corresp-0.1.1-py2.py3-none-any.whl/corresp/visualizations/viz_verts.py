import numpy as np
import os.path as osp
import os


def viz_verts(verts, src_img, dest_img, out_file='keypoints.png'):
    """
    Args:
        verts (2, n_verts, 2)
        src_img (H, W, 3)
        dest_img (H, W, 3)
    """
    import matplotlib.pyplot as plt
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']

    select_idxs = np.random.choice(range(verts.shape[1]),
                                   size=(len(colors),), replace=False)
    select_verts = verts[:, select_idxs]

    plt.figure()
    plt.subplot(1, 2, 1)
    plt.imshow(src_img)
    for i in range(len(colors)):
        plt.scatter(select_verts[0, i, 1], select_verts[0, i, 0],
                    c=colors[i], s=100)

    plt.subplot(1, 2, 2)
    plt.imshow(dest_img)
    for i in range(len(colors)):
        u_dest = select_verts[1, i, 1]
        v_dest = select_verts[1, i, 0]
        plt.scatter(u_dest, v_dest, c=colors[i], s=100)

    plt.savefig(out_file, bbox_inches='tight', pad_inches=0)
    plt.close()
