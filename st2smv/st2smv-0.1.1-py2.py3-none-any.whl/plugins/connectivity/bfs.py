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
import math

import networkx

from . import cone_of_influence
from ... import utils

logger = utils.logging.getLogger(__name__)


def disconnect_digraph(
        dg, limit,
        root=None, untouchable=None,
):
    """

    """
    ## Check the arguments.
    assert isinstance(root, list)
    assert isinstance(untouchable, list)

    ## Compute shortest paths and node depths.
    sp = _shortest_path_length_to_multiple_targets(dg, targets=root)
    if len(sp) <= limit:
        return set()
    depths = {}
    for node in sp:
        depth = sp[node]
        if depth not in depths:
            depths[depth] = set()
        depths[depth].add(node)
    assert depths == depths

    ## Get the target depth.
    target_depth = 0
    total = 0
    while True:
        total += len(depths[target_depth])
        if total >= min(limit, len(sp)):
            break
        else:
            target_depth += 1
            continue

    ## Delete any nodes `deeper` than the `target_depth`.
    deeper = set()
    for depth in range(target_depth + 1, max(depths) + 1):
        deeper |= depths[depth]
    also_deleted = deeper - set(untouchable)
    if len(also_deleted) > 0:
        return also_deleted

    ## Find the "candidate" nodes at or above the `target_depth`.
    candidate_depth = target_depth
    while True:
        if candidate_depth < 0:
            raise cone_of_influence.AbstractionError(
                'Cannot remove nodes below depth 0 (tried {}).'
                .format(candidate_depth)
            )
        candidates = depths[candidate_depth] - set(untouchable)
        if len(candidates) > 0:
            break
        else:
            candidate_depth -= 1
            continue

    ## Delete nodes to disconnect the graph.
    if len(candidates) == 0:
        deleted = set()
    else:
        ## Only delete the "major contributors".
        candidates_with_scores = sorted(
            [
                (x, _candidate_score(dg, root, x, depths))
                for x in candidates
            ],
            key=(lambda c_w_s: c_w_s[1]),
            reverse=True
        )
        deleted = {candidates_with_scores[0][0]}
    ##
    return deleted


def _candidate_score(dg, root, node, depths):
    ## Find the shortest path length from `root` to `node`.
    depth = _shortest_path_length_to_multiple_targets(
        dg, source=node, targets=root
    )

    ## Get the set of variables that are already included in the COI,
    ## up to `depth`.
    already_included = set()
    for d in sorted(depths):
        if d <= depth:
            already_included |= depths[d]
        else:
            break

    ## Get `node`'s additional contribution to the COI.
    node_predecessors = dg.predecessors(node)
    also_included = set(node_predecessors) - already_included

    ## Compute the cost.
    cost = len(also_included)
    return cost


def _shortest_path_length_to_multiple_targets(graph, source=None, targets=None):
    """Wrap `networkx.shortest_path_length` and add the ability to specify
    `targets` as a list of nodes (instead of a single node).

    """
    if isinstance(targets, list):
        ## Multiple targets.
        results = []
        for target in targets:
            try:
                result = networkx.shortest_path_length(
                    graph, source=source, target=target
                )
                results.append(result)
            except networkx.exception.NetworkXNoPath:
                ## `source` is a single node, and it does not have a
                ## path to this `target`; skip it.
                pass
        if source is None:
            ## No source; `results` will contain `dict`s.
            return _merge_length_dicts(results)
        else:
            ## Assume a single source; `results` will contain `int`s.
            return min(results)
    else:
        return networkx.shortest_path_length(
            graph, source=source, target=targets
        )


def _merge_length_dicts(length_dicts):
    assert isinstance(length_dicts, (list, tuple))
    lengths = dict()
    for ld in length_dicts:
        for source_node in ld:
            incumbent = lengths.get(source_node)
            challenger = ld[source_node]
            if incumbent is None:
                lengths[source_node] = challenger
            elif challenger < incumbent:
                lengths[source_node] = challenger
    return lengths


def cut_coi(
        dg, limit,
        root=None, untouchable=None,
):
    """

    """
    ## Check the arguments.
    assert isinstance(root, list)

    ## Make sure not to delete any `root` variables.
    if untouchable is None:
        untouchable = root[:]
    else:
        untouchable = untouchable + root[:]

    ## If the largest COI is larger than `limit`, then delete some
    ## nodes to bring the size of that COI down to `limit`.
    deleted = disconnect_digraph(
        dg, limit,
        root=root, untouchable=untouchable,
    )

    ## Return the set of deleted nodes.
    return deleted


def cut_coi_iterative(
        digraph, limit,
        root=None, untouchable=None,
        already_deleted=None
):
    """

    """
    ## Check the arguments.
    assert isinstance(root, list)
    if already_deleted is None:
        already_deleted = set()

    ## Work with a subgraph.
    coi_nodes = cone_of_influence.digraph_coi(digraph, root)
    dg = digraph.subgraph(coi_nodes)

    ## Remove the `already_deleted` nodes, and recompute the subgraph.
    for ad in already_deleted:
        successors = dg.successors(ad)
        dg.remove_node(ad)
        dg.add_node(ad)
        for s in successors:
            dg.add_edge(ad, s)
    coi_nodes = cone_of_influence.digraph_coi(dg, root)
    dg = dg.subgraph(coi_nodes)

    ## Mark any "leaf" variables in the COI that don't have connection
    ## information (probably input variables in the model) as
    ## untouchable, since deleting them would have no impact.
    u = [x for x in coi_nodes if dg.in_degree(x) == 0]
    if untouchable is None:
        pass
    else:
        u += copy.deepcopy(untouchable)

    ## Iteratively delete nodes and check if the COI limit is met.
    deleted = set()
    iterations = 0
    while True:
        try:
            new_deleted = cut_coi(
                dg, limit,
                root=root, untouchable=(u + list(deleted)),
            )
        except cone_of_influence.AbstractionError:
            new_deleted = set()
        if len(new_deleted) > 0:
            ## Replace the "deleted" nodes.
            for nd in new_deleted:
                successors = dg.successors(nd)
                dg.remove_node(nd)
                dg.add_node(nd)
                for s in successors:
                    dg.add_edge(nd, s)
            ## Update the subgraph.
            coi_nodes = cone_of_influence.digraph_coi(dg, root)
            dg = dg.subgraph(coi_nodes)
            ## Get ready for the next iteration.
            deleted = set.union(deleted, new_deleted)
            iterations += 1
            continue
        else:
            logger.debug('Did not delete any more nodes.')
            break

    ## Get the final COI information, then add the edges back.
    coi = cone_of_influence.digraph_coi(dg, root)

    ## Done.
    logger.debug(
        'After {} iteration(s), deleted {} node(s): {}'
        .format(iterations, len(deleted), deleted)
    )
    return (deleted | already_deleted, coi, iterations)


def get_variable_cuts(
        digraph, node2var,
        coi_vars=None,
        max_coi=100,
        untouchable=None,
):
    """Given the COI graph `digraph`, compute the set of variables that
    should be removed so that the COI rooted at `coi_vars` contains no
    more than `max_coi` variables.  Any variables in `untouchable`
    will not be removed.

    """
    logger.debug('Computing COI cuts for variable(s): {}'.format(coi_vars))

    ## Convert from "variables" (`ir.Var`) to "nodes" (`int`), which
    ## are used for all internal computations.
    var2node = utils.invert_mapping(node2var)
    if coi_vars is None:
        coi_nodes = None
    else:
        coi_nodes = [var2node[x] for x in coi_vars]

    ## Original size.
    size0 = -1
    if coi_nodes is not None:
        coi0 = cone_of_influence.digraph_coi(digraph, coi_nodes)
        size0 = len(coi0)

    ## Cuts.
    assert isinstance(max_coi, int)
    undershoot_tolerance = 0.8
    overshoot_tolerance = 1.0
    deleted = set()
    (deleted, coi, coi_iterations) = cut_coi_iterative(
        digraph, max_coi,
        root=coi_nodes, untouchable=untouchable,
        already_deleted=deleted
    )
    coi_size = len(coi)
    factor = float(coi_size) / float(max_coi)
    nothing_condition = (size0 <= max_coi)
    success_condition = (
        undershoot_tolerance <= factor and factor <= overshoot_tolerance
    )
    if nothing_condition:
        logger.debug(
            'Got a "null" COI reduction ({} -> {}/{})'
            .format(size0, coi_size, max_coi)
        )
    elif success_condition:
        logger.debug(
            'Got a "good" COI reduction ({} -> {}/{}).'.format(
                size0, coi_size, max_coi
            )
        )
    else:
        logger.debug(
            'Got a "bad" COI reduction ({} -> {}/{}).'
            .format(size0, coi_size, max_coi)
        )

    ## Convert from "nodes" back to "variables" and return.
    relevant_deleted = set.intersection(coi, deleted)
    return (
        {node2var[x] for x in relevant_deleted},
        coi_size, size0,
        {node2var[x] for x in coi}
    )
