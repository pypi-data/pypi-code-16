#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Thu 12 Nov 2015 16:35:08 CET 
#

"""
Train the score normalizer

Usage:
  generate_normalizer.py <score_dev> <score_eval> <output-norm>
  generate_normalizer.py -h | --help
Options:
  -h --help           Show this screen.
"""

import bob.measure
import numpy
from .utils import compute_stats, apply_norm


def compute_norm_eer(positives, negatives, mi, ma):

    positives = apply_norm(positives, mi, ma)
    negatives = apply_norm(negatives, mi, ma)

    t = bob.measure.eer_threshold(negatives, positives)
    far, frr = bob.measure.farfrr(negatives, positives, t)
    
    return (far+frr)/2

def compute_norm_far(positives, negatives, mi, ma, far_value=0.01):

    positives = apply_norm(positives, mi, ma)
    negatives = apply_norm(negatives, mi, ma)

    t = bob.measure.far_threshold(negatives, positives, far_value=far_value)
    far, frr = bob.measure.farfrr(negatives, positives, t)
    
    return (far+frr)/2


    
def main():
    from docopt import docopt

    args = docopt(__doc__, version='')

    negatives_dev, positives_dev  = bob.measure.load.split_four_column(args["<score_dev>"])
    negatives_eval, positives_eval = bob.measure.load.split_four_column(args["<score_eval>"])
    filename = args["<output-norm>"]

    mi, ma = compute_stats(numpy.hstack((negatives_dev, positives_dev)))

    print "EER"    
    print "EER in dev - {0}".format(compute_norm_eer(positives_dev.copy(), negatives_dev.copy(), mi, ma))    
    print "EER in eval - {0}".format(compute_norm_eer(positives_eval.copy(), negatives_eval.copy(), mi, ma))

    print "FAR 0.01"
    print "FRR with FAR 0.01 in dev - {0}".format(compute_norm_far(positives_dev.copy(), negatives_dev.copy(), mi, ma))
    print "FRR with FAR 0.01 in dev - {0}".format(compute_norm_far(positives_eval.copy(), negatives_eval.copy(), mi, ma))

    print "FAR 0.001"
    print "FRR with FAR 0.001 in dev - {0}".format(compute_norm_far(positives_dev.copy(), negatives_dev.copy(), mi, ma, far_value=0.001))
    print "FRR with FAR 0.001 in dev - {0}".format(compute_norm_far(positives_eval.copy(), negatives_eval.copy(), mi, ma, far_value=0.001))

    
    hdf5 = bob.io.base.HDF5File(filename, 'w')
    hdf5.set("mi", mi)
    hdf5.set("ma", ma)
    del hdf5    

    print "########"
    print "max {0}".format(ma)
    print "mi {0}".format(mi)    
    

