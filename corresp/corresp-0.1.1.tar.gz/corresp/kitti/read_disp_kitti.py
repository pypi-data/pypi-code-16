import numpy as np
import imageio


def read_disp_kitti(disp_file):
    """
    Returns:
        image of (H, W, 3). The last dimension contains
            (vertical_flow, horizontal_flow, valid).
    
    Returned data has same structure as what read_flow returns.

    Disparity maps are saved as uint16 PNG image. A 0 value indicates an 
    invalid pixel (ie, no ground truth exists, or the estimation algorithm 
    didn't produce an estimate for that pixel). Otherwise, the disparity 
    for a pixel can be computed by converting the uint16 value to float 
    and dividing it by 256.0:

    disp(u,v)  = ((float)I(u,v))/256.0;
    valid(u,v) = I(u,v)>0;
    """
    disp = imageio.imread(disp_file)
    disp = np.asarray(disp).astype(np.float32)

    invalid_idx = disp <= 0
    disp = disp / 256.
    disp[invalid_idx] = 0
    # print disp.shape

    H, W = disp.shape
    u = -1 * disp
    v = np.zeros_like(disp)
    flow = np.stack([v, u, np.zeros((H, W))], axis=2)
    return flow
