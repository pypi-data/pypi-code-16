## Copyright (c) 2016, Blake C. Rawlings.
##
## This file is part of `st2smv`.

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import copy

from ... import ast
from ... import ir
from ... import plugins
from ... import smv
from ... import utils

logger = utils.logging.getLogger(__name__)

## Plugin information.
NAME = 'irrelevant_logic'
ACTIONS = (
    plugins.actions.PROCESS_INDEPENDENT_TESTS,
    plugins.actions.POSTPROCESS,
)
OPTIONS = {}


def generate_pits(converter):
    pit_tmp = converter.assigned | converter.defined
    pit_tmp -= converter.aliases
    pit_tmp -= converter.ivars
    pit_tmp &= converter.unconditional_assignments
    pit_vars = sorted(
        {x for x in pit_tmp if (converter.get_type(x) == ast.BOOLEAN)}
    )

    ##
    alternative_logic = {}
    locations = utils.get_locations(
        converter.logic_ir,
        rule=(lambda x: x == ast.ASSIGN)
    )
    assignments = [
        utils.get_value_at_location(converter.logic_ir, location[:-1])
        for location in locations
    ]
    for assignment in assignments:
        (lhs, rhs) = assignment[1]
        if lhs not in pit_vars:
            ## Don't need the alternative logic.
            continue
        logger.debug('Generating alternative logic for {}'.format(lhs))
        rhs_alternatives = get_rhs_alternatives(rhs)
        if rhs_alternatives is not None:
            assert lhs not in alternative_logic
            alternative_logic[lhs] = rhs_alternatives
    ##

    irrel = {'PIT_PREFIX': 'irrel'}
    spec_types = (
        ('SPEC', 'irrel_spec'),
        ('SYNTH', 'irrel_synth'),
    )
    for var in pit_vars:
        if var not in alternative_logic:
            continue
        assert var not in irrel
        irrel[var] = []
        for pattern in sorted(alternative_logic[var]):
            altvar = '{}_{}'.format(var, pattern)
            irrel[var].append('VAR {} : boolean;'.format(altvar))
            irrel[var].append('INIT {} = {};'.format(altvar, var))
            irrel[var].append(
                'TRANS initializing -> next({} = {});'.format(altvar, var)
            )
            irrel[var].append(
                'TRANS next({} = ({}));'
                .format(
                    altvar,
                    smv.ir_to_expression(alternative_logic[var][pattern])
                )
            )
            for spec_type in spec_types:
                irrel[var].append(
                    '{} NAME {}_{} := AG({} = {});'
                    .format(spec_type[0], spec_type[1], altvar, var, altvar)
                )
    return irrel


def get_rhs_alternatives(tree):
    """Compute "alternative versions" of the IR expression `tree`.

    This returns the `dict` of "alternative" expressions obtained by
    removing terms from `tree`.  The returned `dict` maps strings
    indicating which terms were dropped/kept (for example, the string
    '011' means the first term was dropped, and the other two were
    kept) to the corresponding expression.

    """
    def looks_like_boolean_expression(x):
        if isinstance(x, ir.Var):
            return True
        elif isinstance(x, (tuple, list)):
            if len(x) > 0:
                if x[0] in ast.comparators + (ir.EQ_NUMERIC, ir.NEQ_NUMERIC):
                    return True
        else:
            return False
    ## Generate the replacement `patterns`, based on the total number
    ## of `terms`.
    patterns = []
    locations = utils.get_locations(tree, rule=looks_like_boolean_expression)
    terms = [utils.get_value_at_location(tree, l) for l in locations]
    n = len(terms)
    if n <= 1:
        return None
    for i in range(n):
        pattern = [1] * n
        pattern[i] = 0
        patterns.append(tuple(pattern))

    ## Generate the alternative expressions to match the replacements
    ## `patterns`.
    alternatives = {}
    for pattern in patterns:
        key = ''.join((str(x) for x in pattern))
        alternatives[key] = _get_alternative_logic(
            tree, pattern, locations=locations
        )

    for alt in sorted(alternatives):
        logger.debug('{}: {}'.format(alt, alternatives[alt]))
    return alternatives


def _get_alternative_logic(tree, pattern, locations=None):
    """Delete some of the `terms` from `tree` according to `pattern`."""
    if locations is None:
        assert False
    else:
        terms = [utils.get_value_at_location(tree, l) for l in locations]
    assert len(pattern) == len(locations)

    ## Replace each dropped term with a dummy variable, `dropped`.
    dropped = ir.Var('DROPPED', None)
    while dropped in terms:
        dropped = ir.Var('_' + dropped.label, None)
    replaced = copy.deepcopy(tree)
    for i, p in enumerate(pattern):
        if p == 0:
            ## Drop the term.
            utils.set_value_at_location(replaced, locations[i], dropped)

    ## Reduce `tree`.
    reduced = _reduce_dropped_terms(replaced, dropped)
    return reduced


def _reduce_dropped_terms(tree, dropped):
    """Reduce `tree` by removing all appearances of `dropped`."""
    while True:
        reduced = _reduce_dropped_terms_worker(tree, dropped)
        if reduced == tree:
            break
        else:
            tree = reduced
    if dropped == reduced:
        logger.warning('Computed irrelevant logic with a single term.')
    return reduced


def _reduce_dropped_terms_worker(tree, dropped):
    """Reduce `tree` by removing an appearance of `dropped`."""
    ## Copy `tree` for modification (don't mess up the original).
    reduced = copy.deepcopy(tree)
    ## Find the first appearance of `dropped`.
    locations = utils.get_locations(tree, rule=(lambda x: x == dropped))
    if locations is None:
        return reduced
    if len(locations) == 0:
        return reduced
    location = locations[0]
    assert utils.get_value_at_location(tree, location) == dropped
    ## Find the location (and type) of the enclosing operation.
    op_location = location[:-1]
    while True:
        operation = utils.get_value_at_location(reduced, op_location)
        if operation[0] in ast.binary_operators + ast.unary_operators:
            operator = operation[0]
            op_distance = len(location) - len(op_location)
            break
        else:
            if len(op_location) == 0:
                assert False
            op_location = op_location[:-1]
    if op_distance == 1:
        assert operator in ast.unary_operators
    else:
        assert op_distance == 2
        assert operator in ast.binary_operators
    ## Remove `dropped` from the operation, and simplify.
    if operator in ast.unary_operators:
        if len(op_location) == 0:
            reduced = dropped
        else:
            utils.set_value_at_location(reduced, op_location, dropped)
    elif operator in ast.binary_operators:
        other_location = copy.copy(location)
        other_location[-1] = 1 - other_location[-1]
        new_operation = utils.get_value_at_location(reduced, other_location)
        if len(op_location) == 0:
            reduced = new_operation
        else:
            utils.set_value_at_location(
                reduced, op_location, new_operation
            )
    else:
        assert False
    ## Return the reduced IR tree.
    return reduced


def get_postprocessing_categories():
    return (
        ('Guaranteed Irrelevant Logic', 'irrel_spec', 'true'),
        ('Potential Irrelevant Logic', 'irrel_synth', 'true'),
        ('Guaranteed Relevant Logic', 'irrel_synth', 'false'),
        ('Potential Relevant Logic', 'irrel_spec', 'false'),
    )
