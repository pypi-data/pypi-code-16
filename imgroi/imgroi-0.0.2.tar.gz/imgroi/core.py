__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Oct 28, 2016 15:26$"


import numpy

import mahotas


def label_mask_stack(new_masks, dtype=None):
    """
        Takes a mask stack and replaces them by the max of an enumerated stack.
        In other words, each mask is replaced by a consecutive integer (starts
        with 1 and proceeds to the length of the given axis (0 by default)).
        Afterwards, the max is taken along the given axis.

        Args:
            new_masks(numpy.ndarray):            masks to enumerate
            dtype(type):                         type to use for the label
                                                 matrix (default is int).

        Returns:
            (numpy.ndarray):                     an enumerated stack.

        Examples:

            >>> label_mask_stack(
            ...     numpy.array([[[1, 0, 0, 0],
            ...                   [0, 0, 0, 0],
            ...                   [0, 0, 0, 0],
            ...                   [0, 0, 0, 0]],
            ...
            ...                  [[0, 0, 0, 0],
            ...                   [0, 1, 0, 0],
            ...                   [0, 0, 0, 0],
            ...                   [0, 0, 0, 0]],
            ...
            ...                  [[0, 0, 0, 0],
            ...                   [0, 0, 0, 0],
            ...                   [0, 0, 1, 0],
            ...                   [0, 0, 0, 0]],
            ...
            ...                  [[0, 0, 0, 0],
            ...                   [0, 0, 0, 0],
            ...                   [0, 0, 0, 0],
            ...                   [0, 0, 0, 1]]], dtype=bool)
            ... )
            array([[1, 0, 0, 0],
                   [0, 2, 0, 0],
                   [0, 0, 3, 0],
                   [0, 0, 0, 4]])
    """

    try:
        xrange
    except NameError:
        xrange = range

    if dtype is None:
        dtype = int
    dtype = numpy.dtype(dtype).type


    new_lbl_img = numpy.zeros(
        new_masks.shape[1:],
        dtype=dtype
    )

    for i in xrange(len(new_masks)):
        lbl = new_lbl_img.dtype.type(i + 1)
        numpy.maximum(
            new_lbl_img,
            lbl * new_masks[i],
            out=new_lbl_img
        )

    return new_lbl_img


def find_contours(img):
    """
        Takes an image and extracts contours from the mask.

        Args:
            a_image(numpy.ndarray):            takes an image.

        Returns:
            (numpy.ndarray):                   an array with contours.

        Examples:

            >>> a = numpy.array([[ True,  True, False],
            ...                  [False, False, False],
            ...                  [ True,  True,  True]], dtype=bool)

            >>> find_contours(a)
            array([[ True,  True, False],
                   [False, False, False],
                   [ True,  True,  True]], dtype=bool)

            >>> find_contours(numpy.eye(3))
            array([[ 1.,  0.,  0.],
                   [ 0.,  1.,  0.],
                   [ 0.,  0.,  1.]])

            >>> a = numpy.array([
            ...     [False, False,  True, False, False, False,  True],
            ...     [ True, False, False, False,  True, False, False],
            ...     [ True,  True, False,  True,  True, False,  True],
            ...     [ True, False, False,  True,  True, False, False],
            ...     [ True, False, False, False, False, False, False],
            ...     [False,  True, False, False, False, False,  True],
            ...     [False,  True,  True, False, False, False, False]
            ... ], dtype=bool)

            >>> find_contours(a)
            array([[False, False,  True, False, False, False,  True],
                   [ True, False, False, False,  True, False, False],
                   [ True,  True, False,  True,  True, False,  True],
                   [ True, False, False,  True,  True, False, False],
                   [ True, False, False, False, False, False, False],
                   [False,  True, False, False, False, False,  True],
                   [False,  True,  True, False, False, False, False]], dtype=bool)


    """

    struct = numpy.ones((3,) * img.ndim, dtype=bool)

    mask = (img != 0)
    mask ^= mahotas.erode(
        mask,
        struct
    )

    contours = img * mask

    return contours
