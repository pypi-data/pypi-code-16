import numpy as np


# port sinte/flow_code/MATLAB/readFlowFile.m


def read_flow_sintel(flo_file):
    """Read .flo file in Sintel.

    Returns:
        Float32 image of shape (H, W, 3). The last dimension contains
            (vertical_flow, horizontal_flow, valid).

    Note:
        In the original binary, flows are stored in order of
            (horizontl_flow, vertical_flow).
            Here, they are in the opposite order.
    """

    with open(flo_file, 'rb') as f:
        magic = np.fromfile(f, np.float32, count=1)
        if 202021.25 != magic:
            print 'Magic number incorrect. Invalid  .flo file'
        else:
            W = np.asscalar(np.fromfile(f, np.int32, count=1))
            H = np.asscalar(np.fromfile(f, np.int32, count=1))

            data = np.fromfile(f, np.float32, count=2 * W * H)
            data = data.reshape(H, W, 2)

    ret = np.zeros((H, W, 3), np.float32)
    # find valid pixels
    valid = np.max(data, axis=2) < 1e9
    # last dimension:  (vertical disp, horizontal disp, valid)
    ret[:, :, 0] = data[:, :, 1]
    ret[:, :, 1] = data[:, :, 0]
    ret[:, :, 2] = valid
    return ret
