"""
Define helper routines for interacting with the Brillouin
zone
"""

import numpy as np


class BrillouinZone(SuperCellChild):
    """ Class to hold k-points and associated weights """

    def __init__(self, sc, *args, **kwargs):
        """
        Initialize the `BrillouinZone` object.

        Parameters
        ----------
        sc : `SuperCell` or class with `.sc` as `SuperCell`

        """
        if isinstance(sc, SuperCell):
            self.set_supercell(sc)
        else:
            self.set_supercell(sc.sc)

        self._k = np.zeros([1, 3], np.float64)
        self._w = np.zeros([1], np.float64) + 1.

    @property
    def k(self):
        """ k-points in the Brillouin zone """
        return self._k

    @property
    def w(self):
        """ weights of k-points in the Brillouin zone """
        return self._w
