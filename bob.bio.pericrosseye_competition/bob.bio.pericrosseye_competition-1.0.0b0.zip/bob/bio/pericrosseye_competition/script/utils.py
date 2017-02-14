"""
Simple score normalization
"""

import numpy

def compute_stats(scores):
    mi = numpy.min(scores)
    ma = numpy.max(scores)
    
    return mi, ma
    
def apply_norm(X, mi, ma):
    return (X - mi) / (ma-mi)


