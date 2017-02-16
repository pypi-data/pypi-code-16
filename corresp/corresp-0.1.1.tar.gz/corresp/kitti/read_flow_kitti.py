import imageio
import numpy as np


def read_flow_kitti(flow_file):
    """
    Returns:
        Float32 image of shape (H, W, 3). The last dimension contains
            (vertical_flow, horizontal_flow, valid).

    Note:
        In the original binary, flows are stored in order of 
            (horizontl_flow, vertical_flow).
            Here, they are in the opposite order.

    Read kitti flow from .png file

    Optical flow maps are saved as 3-channel uint16 PNG images: The first channel
    contains the u-component, the second channel the v-component and the third
    channel denotes if a valid ground truth optical flow value exists for that
    pixel (1 if true, 0 otherwise). To convert the u-/v-flow into floating point
    values, convert the value to float, subtract 2^15 and divide the result by 64:

    flow_u(u,v) = ((float)I(u,v,1)-2^15)/64.0;
    flow_v(u,v) = ((float)I(u,v,2)-2^15)/64.0;
    valid(u,v)  = (bool)I(u,v,3);
    """
    import matplotlib.pyplot as plt
    import matplotlib.colors as cl
    flow = imageio.imread(flow_file)
    flow = np.asarray(flow).astype(np.float32)

    invalid_idx = (flow[:, :, 2] == 0)
    flow[:, :, :2] = (flow[:, :, :2] - 2 ** 15) / 64.0
    flow[invalid_idx, :2] = 0
    ret = np.zeros_like(flow)
    ret[:, :, 0] = flow[:, :, 1]
    ret[:, :, 1] = flow[:, :, 0]
    ret[:, :, 2] = flow[:, :, 2]
    return ret
