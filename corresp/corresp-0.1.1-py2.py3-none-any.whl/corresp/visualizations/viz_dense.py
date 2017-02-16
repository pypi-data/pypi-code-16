import numpy as np
from corresp.visualizations.viz_flow import viz_flow


def get_colorwheel_img(H, W):
    xx, yy = np.meshgrid(range(W), range(H))
    u = xx - W/2
    v = yy - H/2
    flow = np.stack([v, u, np.zeros_like(u)], axis=2)
    colorwheel = viz_flow(flow)
    return colorwheel


def _viz_dense(verts, H, W):
    n_verts = verts.shape[1]
    colorwheel = get_colorwheel_img(H, W)

    # map colorwheel color using vert_pairs
    dest_colors = np.zeros((H, W, 3), dtype=np.uint8)
    for i in range(n_verts):
        dest_colors[verts[1, i, 0], verts[1, i, 1]] =\
            colorwheel[verts[0, i, 0], verts[0, i, 1]]
    src_colors = colorwheel
    return src_colors, dest_colors


def viz_dense(verts, src_img, dest_img, out_file, src_mask=None, dst_mask=None):
    """
    Args:
        verts (2, H*W, 2)
        src_img (H, W, 3)
        dest_img (H, W, 3)

    """
    import matplotlib.pyplot as plt
    H, W, _ = src_img.shape

    src_colors, dest_colors = _viz_dense(verts, H, W)

    f = plt.figure(figsize=(20, 65))
    f.set_figheight(12)
    f.set_figwidth(30)
    plt.subplot(2, 2, 1)
    plt.imshow(src_img)
    plt.imshow(src_colors, alpha=.5, interpolation='None')

    plt.subplot(2, 2, 2)
    plt.imshow(dest_img)
    plt.imshow(dest_colors, alpha=.5, interpolation='None')  # gray means no matching

    plt.subplot(2, 2, 3)
    plt.imshow(src_colors, interpolation='None')  # gray means no matching

    plt.subplot(2, 2, 4)
    plt.imshow(dest_colors, interpolation='None')  # gray means no matching

    plt.tight_layout()
    plt.savefig(out_file, bbox_inches='tight', pad_inches=0)
    plt.close()


def convert_to_vert_img(src_verts, dest_verts, H, W):
    """Used as a helper for vis_dense
    Args:
        src_verts:  (n_verts, 2)
        dest_verts:  (n_verts, 2)

    (src_verts_visible, dst_verts_visible) --> (2, H, W)
    """
    vert_img = np.zeros((2, H, W))

    assert len(src_verts) == len(dest_verts)
    for src_vert, dest_vert in zip(src_verts, dest_verts):
        vert_img[:, dest_vert[0], dest_vert[1]] = src_vert
    return vert_img


if __name__ == '__main__':
    import imageio
    import os.path as osp

    src_img = imageio.imread(osp.expanduser(
        '~/data/datasets/kitti_flow/training/image_2/000000_10.png'))
    dest_img = imageio.imread(osp.expanduser(
        '~/data/datasets/kitti_flow/training/image_2/000000_11.png'))
    H, W, _ = src_img.shape
    y = np.random.choice(range(H), size=(H, W))
    x = np.random.choice(range(W), size=(H, W))

    vert_img = np.stack([y, x])
    viz_dense(vert_img, src_img, dest_img, 'sample')
