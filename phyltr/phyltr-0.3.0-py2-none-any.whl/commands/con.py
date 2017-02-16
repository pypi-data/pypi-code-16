import fileinput
import sys

import phyltr.utils.cladeprob

import ete2

def run():

    # Read trees and compute clade probabilities
    trees = []
    cp = phyltr.utils.cladeprob.CladeProbabilities()
    for line in fileinput.input():
        t = ete2.Tree(line)
        trees.append(t)
        cp.add_tree(t)
    cp.compute_probabilities()

    # Find max clade prob tree
    max_prob = -sys.float_info.max
    for t in trees:
        prob = cp.get_tree_prob(t)
        if prob > max_prob:
            max_prob = prob
            best_tree = t

    # Annotate max clade prob tree with clade supports
    cp.annotate_tree(best_tree)

    # Output
    print best_tree.write()

    # Done
    return 0
