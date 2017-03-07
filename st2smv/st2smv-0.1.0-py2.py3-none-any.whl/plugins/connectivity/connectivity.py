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

from . import bfs
from ... import ast
from ... import plugins
from ... import utils

logger = utils.logging.getLogger(__name__)

## Plugin information.
NAME = 'connectivity'
ACTIONS = (
    plugins.actions.ABSTRACTION,
    plugins.actions.INFLUENCE,
)
OPTIONS = {
    'max_coi': (
        int,
        (
            'set the maximum cone-of-influence (COI) size, '
            'and compute COI cuts to enforce that limit'
        )
    )
}
MAX_COI_DEFAULT = 100


class Connectivity(object):
    """A class to analyze and manipulate the connections between the
    variables in a ST model.

    """
    def __init__(self, converter):
        ## Copy over the connection information.
        self.connections = copy.deepcopy(converter.connections)
        ## Set up a map from variables in `converter.connections` to a
        ## simpler type.
        self.var2node = self._generate_var2node_mapping()
        self.node2var = self._generate_node2var_mapping()
        if True:
            ## TODO: remove this test
            assert self.node2var == utils.invert_mapping(self.var2node)
        ## Produce a (di)graph from the connectivity information.
        self.digraph = self._connectivity_digraph()

    def _generate_var2node_mapping(self):
        """Map variables in `self.connections` to a simpler type (`int` for
        now).  This should help the performance.

        """
        mapping = {}
        mapped = set()
        n = 0
        for key in self.connections:
            if key in mapped:
                pass
            else:
                mapping[key] = n
                mapped.add(key)
                n += 1
            for connection in self.connections[key]:
                if connection in mapped:
                    pass
                else:
                    mapping[connection] = n
                    mapped.add(connection)
                    n += 1
        return mapping

    def _generate_node2var_mapping(self):
        """This has to be called after `self.var2node` is set up."""
        mapping = {}
        for var in self.var2node:
            node = self.var2node[var]
            mapping[node] = var
        return mapping

    def _connectivity_digraph(self):
        """Use the information in `self.connections` to generate a
        connectivity graph (a `networkx.DiGraph` object).

        """
        digraph = networkx.DiGraph()
        for to_var in self.connections:
            for from_var in self.connections[to_var]:
                digraph.add_edge(self.var2node[from_var], self.var2node[to_var])
        return digraph


@utils.timing(log_fun=logger.info, log_text='Computed COI cuts: {:.2f}s')
def compute_abstractions(converter):
    """Compute "COI cuts" to simplify the model.

    Returns a `dict` that maps each of the variables in `coi_vars` to
    COI cuts that enforce `max_coi` for that variable.

    """
    ## Mark some variables untouchable.
    untouchable = get_untouchable(converter)
    ## Get the set of variables that might need COI cuts.
    coi_variables = get_coi_variables(converter)
    ## Actually compute the COI cut information.
    coi_cuts = {}
    conn = Connectivity(converter) # TODO: avoid creating this twice
    n = len(coi_variables)
    alive_increment = max(1, int(n / 10))
    if 'coi' not in converter.special_variables:
        converter.special_variables['coi'] = {}
    for idx, variable in enumerate(coi_variables):
        if idx % alive_increment == 0:
            logger.info(
                'Computing COI cuts for variable {}/{}'.format(idx+1, n)
            )
        (deleted, size, size0, target, coi) = get_variable_cuts(
            conn.digraph, conn.node2var,
            [variable], converter.plugin_options, untouchable,
        )
        coi_cuts[variable] = {
            'deleted': sorted(deleted),
            'size': size,
            'original size': size0,
            'target': target,
            'coi': sorted(coi),
        }
        converter.special_variables['coi'][variable] = coi
    ## Return the COI cut information.
    return ('coi_cuts', coi_cuts)


def get_variable_cuts(
        digraph, node2var, coi_vars, plugin_options, untouchable, method=bfs
):
    """This is a very thin wrapper to compute COI cuts using `method`."""
    target = get_max_coi(plugin_options)
    (deleted, size, size0, coi) = method.get_variable_cuts(
        digraph, node2var,
        coi_vars=coi_vars,
        max_coi=target,
        untouchable=untouchable
    )
    return (deleted, size, size0, target, coi)


def get_max_coi(plugin_options):
    max_coi = plugin_options.get('max_coi')
    if max_coi is None:
        logger.warning(
            'Maximum COI size was not specified '
            '(with the "max_coi=n" plugin option), '
            'defaulting to {}'
            .format(MAX_COI_DEFAULT)
        )
        max_coi = MAX_COI_DEFAULT
    return max_coi


def get_untouchable(converter):
    """Get the set of variables that should not be abstracted."""
    untouchable = []
    might_be_untouchable = set.union(
        converter.referenced, converter.aliases, converter.trivial,
        converter.defined, converter.assigned
    )
    untouchable += [
        x for x in might_be_untouchable if converter.is_untouchable(x)
    ]
    for plugin in plugins.actions.get_active_plugins(
            converter.loaded_plugins, plugins.actions.UNTOUCHABLE
    ):
        untouchable += [
            x
            for x in might_be_untouchable
            if plugin.is_untouchable(converter, x)
        ]
        logger.debug(
            'Marked variables "untouchable" '
            'according to the "{}" plugin.'
            .format(plugin.NAME)
        )
    untouchable_not_boolean = {
        x
        for x in might_be_untouchable
        if (converter.get_type(x) != ast.BOOLEAN)
    }
    untouchable += list(untouchable_not_boolean)
    return untouchable


def get_coi_variables(converter):
    """Get the set of variables that might need COI cuts."""
    variables = converter.assigned | converter.defined
    numeric_variables = {
        x
        for x in variables
        if (converter.get_type(x) == ast.NUMERIC)
    }
    if True:
        ## TODO: remove this check.
        numeric_variables_old = {
            x
            for x in variables
            if (converter.is_numeric(x) or converter.is_numeric(x.label))
        }
        assert numeric_variables == numeric_variables_old
    return variables - numeric_variables


def get_coi_info(converter):
    """Get the info that is needed to compute COI cuts."""
    conn = Connectivity(converter) # TODO: avoid creating this twice
    untouchable = set()
    for variable in get_untouchable(converter):
        node = conn.var2node.get(variable)
        if node is not None:
            untouchable.add(node)
    return {
        'edges': conn.digraph.edges(),
        'node2var': conn.node2var,
        'untouchable': sorted(untouchable),
    }


def get_cone_of_influence(converter, variable):
    return converter.special_variables['coi'][variable]
