from __future__ import division, absolute_import, print_function

import numpy as np


def _circle_rect_pvol(center, radius, corners, samples=10000):
    """
    Monte Carlo estimation of circle/rectangle intersection.

    Parameters
    ----------
    center : length-2 iterable of floats
        Center of the circle (row, column).
    radius : float
        Radius of the circle.
    corners : (4, 2) ndarray of floats
        Corner coordinates, clockwise from upper left.
    samples : int
        Number of random samples; more results in a better estimation.

    Returns
    -------
    intersection : float
        Fraction of rectangle described by `corners` which is
        the intersection of said rectangle and the circle.
    """
    r = np.random.uniform(low=corners[0, 0], high=corners[2, 0], size=samples)
    c = np.random.uniform(low=corners[0, 1], high=corners[1, 1], size=samples)
    levelset = (r - center[0])**2 + (c - center[1])**2 - radius**2 < 0
    return levelset.sum() / samples


def disk(rr, cc, center, radius, precision=0.0001):
    """
    Return a circle with partial volumes calculated.

    Parameters
    ----------
    rr : (M, N) ndarray of floats
        Row point coordinates.
    cc : (M, N) ndarray of floats
        Column point coordinates.
    center : length-2 iterable of floats
        Center of the circle (row, column).
    radius : float
        Radius of the circle.
    precision : float, must be << 1
        Desired upper bound for error in fractional partial volumes.
        Must be << 1.  Lower values (higher precision) require additional
        computation time.

    Returns
    -------
    disk : (M, N) ndarray of floats
        Circular structuring element with partial volumes, i.e.,
        each point carries a value on the range [0, 1] representing
        the fraction of the rectangular space it occupies which the
        circle intersects.

    Notes
    -----
    All input values should carry consistent units. The partial
    volumes are closely approximated via Monte Carlo simulation.
    """
    stepr = rr[1, 0] - rr[0, 0]
    stepc = cc[0, 1] - cc[0, 0]

    # Padded array of point indices half-between all pixel centers
    rrr = np.pad(rr[:, 0] - stepr/2, (0, 1),
                 mode='constant', constant_values=rr[-1, 0] + stepr/2)
    ccc = np.pad(cc[0, :] - stepc/2, (0, 1),
                 mode='constant', constant_values=cc[0, -1] + stepc/2)

    corners = np.zeros(shape=(4, 2))

    # The partial volume array
    disk = np.zeros_like(rr, dtype=np.float64)

    for i in range(disk.shape[0]):
        for j in range(disk.shape[1]):
            # Corners clockwise from upper left
            corners[:, 0] = [rrr[i], rrr[i], rrr[i + 1], rrr[i + 1]]
            corners[:, 1] = [ccc[j], ccc[j + 1], ccc[j + 1], ccc[j]]

            disk[i, j] = _circle_rect_pvol(center, radius, corners,
                                           samples=int(1 / precision))

    return disk


def disk_simple(radius, precision=0.0001):
    """
    A centered disk of specified radius.

    Parameters
    ----------
    radius : float
        Radius of desired disk, presumed to be in coordinate units.
    precision : float, must be << 1
        Desired upper bound for error in fractional partial volumes.
        Must be << 1.  Lower values (higher precision) require additional
        computation time.

    Returns
    -------
    disk : (M, N) ndarray of floats
        Circular partial volume structuring element with specified radius.
    """
    center = np.ceil(radius)
    rr, cc = np.mgrid[0:center*2 + 1, 0:center*2 + 1]

    return disk(rr, cc, (center, center), radius, precision)


# END 2D
##########
# BEGIN 3D


def _sphere_rectprism_pvol(center, radius, origin, deltas, samples=10000):
    """
    Monte Carlo estimation of sphere/rectangular prism intersection.

    Parameters
    ----------
    center : length-3 iterable of floats
        Center of the sphere (row, column, depth).
    radius : float
        Radius of the sphere.
    origin : length-3 iterable of floats
        Lowest valued set of coordinates defining a point on the rectangular
        prism.
    deltas : length-3 iterable of floats
        The size of the rectangular prism in (r, c, z) dimensions.
    samples : int
        Number of random samples; more results in a better estimation.

    Returns
    -------
    intersection : float
        Fraction of rectangle described by `corners` which is
        the intersection of said rectangle and the sphere.
    """
    r = np.random.uniform(low=origin[0], high=origin[0] + deltas[0],
                          size=samples)
    c = np.random.uniform(low=origin[1], high=origin[1] + deltas[1],
                          size=samples)
    z = np.random.uniform(low=origin[2], high=origin[2] + deltas[2],
                          size=samples)

    levelset = ((r - center[0])**2 +
                (c - center[1])**2 +
                (z - center[2])**2) - radius**2 < 0

    return levelset.sum() / samples


def sphere(rr, cc, zz, center, radius, precision=0.0001):
    """
    Return a sphere with partial volumes calculated.

    Parameters
    ----------
    rr : (M, N, P) ndarray of floats
        Row point coordinates.
    cc : (M, N, P) ndarray of floats
        Column point coordinates.
    zz : (M, N, P) ndarray of floats
        Depth point coordinates.
    center : length-3 iterable of floats
        Center of the sphere (row, column, depth).
    radius : float
        Radius of the sphere.
    precision : float, must be << 1
        Desired upper bound for error in fractional partial volumes.
        Must be << 1.  Lower values (higher precision) require additional
        computation time.

    Returns
    -------
    sphere : (M, N) ndarray of floats
        Spherical structuring element with partial volumes, i.e.,
        each point carries a value on the range [0, 1] representing
        the fraction of the rectangular space it occupies which the
        sphere intersects.

    Notes
    -----
    All input values should carry consistent units. The partial
    volumes are closely approximated via Monte Carlo simulation.
    """
    stepr = rr[1, 0, 0] - rr[0, 0, 0]
    stepc = cc[0, 1, 0] - cc[0, 0, 0]
    stepz = zz[0, 0, 1] - zz[0, 0, 0]

    # Padded array of point indices half-between all pixel centers
    rrr = np.pad(rr[:, 0, 0] - stepr/2, (0, 1),
                 mode='constant', constant_values=rr[-1, 0, 0] + stepr/2)
    ccc = np.pad(cc[0, :, 0] - stepc/2, (0, 1),
                 mode='constant', constant_values=cc[0, -1, 0] + stepc/2)
    zzz = np.pad(zz[0, 0, :] - stepz/2, (0, 1),
                 mode='constant', constant_values=zz[0, 0, -1] + stepz/2)

    # The partial volume array
    sphere = np.zeros_like(rr, dtype=np.float64)

    it = np.nditer(sphere, flags=['multi_index'])
    deltas = (stepr, stepc, stepz)

    while not it.finished:
        corner = (rrr[it.multi_index[0]],
                  ccc[it.multi_index[1]],
                  zzz[it.multi_index[2]])

        sphere[it.multi_index] = _sphere_rectprism_pvol(
            center, radius, corner, deltas,
            samples=int(1 / precision))

        it.iternext()

    return sphere


def sphere_simple(radius, precision=0.0001):
    """
    A centered sphere of specified radius.

    Parameters
    ----------
    radius : float
        Radius of desired sphere, presumed to be in coordinate units.
    precision : float, must be << 1
        Desired upper bound for error in fractional partial volumes.
        Must be << 1.  Lower values (higher precision) require additional
        computation time.

    Returns
    -------
    sphere : (M, N, P) ndarray of floats
        Spherical partial volume structuring element with specified radius.
    """
    center = np.ceil(radius)
    extent = center*2 + 1
    rr, cc, zz = np.mgrid[0:extent, 0:extent, 0:extent]

    return sphere(rr, cc, zz, (center, center, center), radius, precision)
