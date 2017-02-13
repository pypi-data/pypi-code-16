from __future__ import division, print_function

from .base_pvm import dilate_pvm, erode_pvm


def close_pvm(image, selem):
    """
    Close image by structuring element with partial volume morphology.

    Parameters
    ----------
    im : ndarray
        Input array to be dilated.
    selec : ndarray
        Structuring element defining the local region to dilate `image`.
        Must have same rank as `image`.

    Returns
    -------
    closed : ndarray
        Closed version of `image`. Returned as floating point with values
        ranging from [0, 1]. Fractional values represent partial volumes.

    Notes
    -----
    For further binary analysis, return the resultant image to boolean with
    ``dilated > 0.5``. However, if other morphological operations happen
    subsequent to this in your workflow, return to boolean only after all
    are complete.
    """
    return erode_pvm(dilate_pvm(image, selem), selem)


def open_pvm(image, selem):
    """
    Open image by structuring element with partial volume morphology.

    Parameters
    ----------
    im : ndarray
        Input array to be dilated.
    selec : ndarray
        Structuring element defining the local region to dilate `image`.
        Must have same rank as `image`.

    Returns
    -------
    closed : ndarray
        Closed version of `image`. Returned as floating point with values
        ranging from [0, 1]. Fractional values represent partial volumes.

    Notes
    -----
    For further binary analysis, return the resultant image to boolean with
    ``dilated > 0.5``. However, if other morphological operations happen
    subsequent to this in your workflow, return to boolean only after all
    are complete.
    """
    return dilate_pvm(erode_pvm(image, selem), selem)
