#!/usr/bin/env python

from numpy import sqrt
import numpy as np
import sys

def compute_rms(a):
    """
      Computes the root mean square.
    """
    N = len(a)
    #a2 = np.power(a,2)
    #return np.linalg.norm(a)/np.sqrt(N)
    return np.sqrt(np.mean(a*a ))

def compute_mean_rel_error(a,b):
    """
      Computes the mean relative error.
    """
    return np.mean(np.abs((a-b)/a))

def compute_max_rel_error(a,b):
    """
      Computes the max relative error.
    """
    return np.amean(np.abs((a-b)/a))

