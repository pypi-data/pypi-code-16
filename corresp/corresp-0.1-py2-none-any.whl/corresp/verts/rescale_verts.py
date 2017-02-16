import numpy as np


def downscale_verts(verts, in_H, in_W, out_H, out_W):
    scale_H = float(out_H) / in_H
    scale_W = float(out_W) / out_W
    assert scale_H == scale_H
    scale = scale_H
    
    verts_out = np.zeros_like(verts, dtype=np.int32)
    verts_out[:, 0] = np.clip(
        verts[:, 0] * scale, 0, out_H - 1).astype(np.int32)
    verts_out[:, 1] = np.clip(
        verts[:, 1] * scale, 0, out_W - 1).astype(np.int32)

    #verts_out = turn_flattened_coord(
    #    verts_out, (out_H, out_W)).astype(np.int32)

    return verts_out


def upscale_verts(verts, in_H, in_W, out_H, out_W):
    """
    Args:
        verts (2, n_verts, 2)
        in_H (int)
        in_W (int)
        out_H (int)
        out_W (int)

    Return:
        (2, n_verts, 2)
        
    """
    outs = []
    for vert in verts:
        outs.append(upscale_verts_single(vert, in_H, in_W, out_H, out_W))
    return np.stack(outs)
        

def upscale_verts_single(verts, in_H, in_W, out_H, out_W):
    """
    Args:
        verts (n_verts, 2)
        in_H (int)
        in_W (int)
        out_H (int)
        out_W (int)

    Return:
        (n_verts, 2)
        
    """
    n_verts = verts.shape[0]
    scale_H = out_H / in_H
    scale_W = out_W / in_W

    assert scale_H == scale_W
    #assert out_H % in_H == 0
    #assert out_W % in_W == 0

    out_verts = []
    for i in range(n_verts):
        for hh in range(scale_H):
            for ww in range(scale_W):
                y = np.clip(verts[i, 0] * scale_H + hh, a_min=0, a_max=out_H-1)
                x = np.clip(verts[i, 1] * scale_W + ww, a_min=0, a_max=out_W-1)
                out_verts.append(np.stack((y, x), axis=0))
    out_verts = np.stack(out_verts, axis=0)
    return out_verts
