## Copyright (c) 2015-2016, Blake C. Rawlings.
##
## This file is part of `st2smv`.

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import copy

import networkx

from ... import utils

logger = utils.logging.getLogger(__name__)


class AbstractionError(Exception):
    """An error when computing COI abstractions."""


def digraph_coi(dg, root):
    """Compute the cone of influence of `root`."""
    coi = set()
    for var in root:
        try:
            new_targets = networkx.algorithms.ancestors(dg, var)
        except networkx.NetworkXError:
            logger.warning('Unknown COI root node: {}'.format(var))
            new_targets = set()
        coi = set.union(coi, new_targets)
        coi.add(var)
    return coi


def ancestor_info(dg, targets, untouchable):
    """Get statistics about how the number of ancestors grows with search
    depth.

    """
    ## Convert to a standard form.
    if isinstance(targets, utils.six.string_types):
        targets = [targets]
    if untouchable is None:
        untouchable = []
    ## Get the shortest paths to the *set* of nodes, `target`.
    sp = {}
    for target in targets:
        sp_part = networkx.algorithms.shortest_path_length(
            dg, target=target
        )
        for u in untouchable:
            if u in sp_part:
                sp_part.pop(u)
        for source in sp_part:
            if source not in sp:
                sp[source] = sp_part[source]
            elif sp_part[source] < sp[source]:
                sp[source] = sp_part[source]
    ## Check how many nodes are "pulled in" as the path length
    ## increases.
    sp_ = copy.deepcopy(sp)
    depths = []
    i = 0
    while len(sp_) > 0:
        hit = []
        for key in sp_:
            if sp_[key] <= i:
                hit.append(key)
        depths.append(len(hit))
        for h in hit:
            sp_.pop(h)
        i += 1
    depths.append(len(sp_))
    ##
    return (sp, depths)
