from __future__ import division, print_function

import numpy as np
import scipy.ndimage as ndi


def dilate_pvm(image, selem):
    """
    Dilate image by structuring element with partial volume morphology.

    Parameters
    ----------
    im : ndarray
        Input array to be dilated.
    selec : ndarray
        Structuring element defining the local region to dilate `image`.
        Must have same rank as `image`.

    Returns
    -------
    dilated : ndarray
        Dilated version of `image`. Returned as floating point with values
        ranging from [0, 1]. Fractional values represent partial volumes.

    Notes
    -----
    For further binary analysis, return the resultant image to boolean with
    ``dilated > 0.5``. However, if other morphological operations happen
    subsequent to this in your workflow, return to boolean only after all
    are complete.

    Uses SciPy.NDImage's `correlate` with `mode='reflect'` under
    the hood.
    """
    assert len(image.shape) == len(selem.shape), "Image and region must have " \
                                                 "identical dimensionality."
    dilated = ndi.correlate(image.astype(np.float64), selem.astype(np.float64),
                            mode='reflect')
    return np.minimum(dilated, 1.0)


def erode_pvm(image, selem):
    """
    Erode image by structuring element with partial volume morphology.

    Parameters
    ----------
    image : ndarray
        Input array to be eroded.
    selec : ndarray
        Structuring element defining the local region to erode `image`.
        Must have same rank as `image`.

    Returns
    -------
    eroded : ndarray
        Eroded version of `image`. Returned as floating point with values
        ranging from [0, 1]. Fractional values represent partial volumes.

    Notes
    -----
    For further binary analysis, return the resultant image to boolean with
    ``eroded > 0.5``. However, if other morphological operations happen
    subsequent to this in your workflow, return to boolean only after all
    are complete.

    Uses SciPy.NDImage's `correlate` with `mode='reflect'` under
    the hood.
    """
    assert len(image.shape) == len(selem.shape), "Image and region must have " \
                                                 "identical dimensionality."
    eroded = ndi.correlate(1 - image.astype(np.float64), selem.astype(np.float64),
                           mode='reflect')
    eroded = 1. - eroded  # Invert

    return np.maximum(eroded, 0.0)
