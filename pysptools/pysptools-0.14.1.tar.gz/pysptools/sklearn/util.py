#

import numpy as np
from sklearn import preprocessing


def _convert2D(M):
    h, w, numBands = M.shape
    return np.reshape(M, (w*h, numBands))


def hyper_scale(M):
    """
    Center a hyperspectral image to the mean and 
    component wise scale to unit variance.
    
    Call scikit-learn preprocessing.scale()
    """
    h, w, numBands = M.shape
    X = np.reshape(M, (w*h, numBands))
    X_scaled = preprocessing.scale(X)
    return np.reshape(X_scaled, (h, w, numBands))


def shape_to_XY(M_list, cmap_list):
    """
    Receive as input a hypercubes list and the corresponding
    masks list. The function reshape and concatenate both to create the X and Y
    arrays.

    Parameters:
        M_list: `numpy array list`
            A list of HSI cube (m x n x p).

        cmap_list: `numpy array list`
            A list of class map (m x n), as usual the classes
            are numbered: 0 for the background, 1 for the first class ...
    """
    def convert2D(M):
        h, w, numBands = M.shape
        return np.reshape(M, (w*h, numBands))

    i = 0
    for m,msk in zip(M_list, cmap_list):
        x = convert2D(m)
        y = np.reshape(msk, msk.shape[0]*msk.shape[1])
        if i == 0:
            X = x
            Y = y
            i = 1
        else:
            X = np.concatenate((X, x))
            Y = np.concatenate((Y, y))
    return X,Y
