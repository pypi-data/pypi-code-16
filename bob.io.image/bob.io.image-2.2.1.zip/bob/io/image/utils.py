#!/usr/bin/env python


def to_matplotlib(img):
    '''Returns a view of the image compatible with matplotlib.

    Parameters:
        img (numpy.ndarray): A 2 or 3 dimensional array containing an image in
            bob style: For a 2D array (grayscale image) should be ``(y, x)``;
            For a 3D array (color image) should be ``(n, y, x)``.

    Returns:
        numpy.ndarray: A view of the ``img`` compatible with
            :py:func:`matplotlib.pyplot.imshow`.
    '''
    import numpy as np

    if img.ndim == 3:
        return np.moveaxis(img, 0, -1)
    else:
        return img


def imshow(img, cmap=None, **kwargs):
    '''Plots the images that are returned by :py:func:`bob.io.base.load`

    Parameters:
        img (numpy.ndarray): A 2 or 3 dimensional array containing an image in
            bob style: For a 2D array (grayscale image) should be ``(y, x)``;
            For a 3D array (color image) should be ``(n, y, x)``.
        cmap (matplotlib.colors.Colormap): Colormap, optional, default: ``None``.
            If ``cmap`` is ``None`` and ``img.ndim`` is 2, defaults to 'gray'.
            ``cmap`` is ignored when ``img`` has RGB(A) information.
        kwargs: These are passed directly to :py:func:`matplotlib.pyplot.imshow`
    '''
    import matplotlib.pyplot as plt

    if cmap is None and img.ndim == 2:
        cmap = 'gray'

    plt.imshow(to_matplotlib(img), cmap=cmap, **kwargs)
