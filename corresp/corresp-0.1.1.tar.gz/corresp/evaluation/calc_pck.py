import numpy as np


def calc_pck(obtained, expected, threshold=30):
    """Calculate PCK@threshold

    PCK stands for "Percentage of Correct Keypoints"

    Args:
        obtained (n, 2)
        expected (n, 2)

    """
    m = obtained.shape[0]
    n = expected.shape[0]
    assert m == n

    difference = dist_keypoints(obtained, expected)

    pck_accuracy = np.mean(difference < threshold)
    return pck_accuracy


def dist_keypoints(obtained, expected):
    """
    Args:
        obtained (n, 2)
        expected (n, 2)
    """
    difference = np.sum(np.abs(obtained - expected), axis=1)
    return difference


def vis_dist_keypoints(obtained, expected, H, W):
    img = np.zeros((H, W))
    img[expected[:, 0], expected[:, 1]] = dist_keypoints(obtained, expected)
    return img
