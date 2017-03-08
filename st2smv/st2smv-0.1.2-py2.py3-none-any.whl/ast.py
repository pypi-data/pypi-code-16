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
import itertools
import json
import os
import pprint

from . import plugins
from . import utils

logger = utils.logging.getLogger(__name__)

## Assignment.
ASSIGN = 'ASSIGN'

## Calls.
CALL = 'CALL'
FUNCTION_BLOCK_CALL = 'FUNCTION_BLOCK_CALL'

## Function block call arguments.
FBARG = 'FBARG'
FBOUT = 'FBOUT'
function_block_operators = (FBARG, FBOUT)

## Comparison.
LT = '<'
LEQ = '<='
GT = '>'
GEQ = '>='
NEQ = '<>'
EQ = '='
inequality_comparators = (LT, LEQ, GT, GEQ)
equality_comparators = (NEQ, EQ)
comparators = inequality_comparators + equality_comparators

## Boolean operators.
AND = 'AND'
OR = 'OR'
XOR = 'XOR'
NOT = 'NOT'
binary_boolean_operators = (AND, OR, XOR)
unary_boolean_operators = (NOT,)
boolean_operators = binary_boolean_operators + unary_boolean_operators

## Arithmetic operators.
ADD = '+'
SUB = '-'
MLT = '*'
DIV = '/'
EXP = '**'
MOD = 'MOD'
NEG = 'NEG'
binary_arithmetic_operators = (ADD, SUB, MLT, DIV, EXP, MOD)
unary_arithmetic_operators = (NEG,)
arithmetic_operators = binary_arithmetic_operators + unary_arithmetic_operators

## Higher level "operators".
CONJUNCTION = 'CONJUNCTION'
DISJUNCTION = 'DISJUNCTION'

## Values.
TRUE = 'TRUE'
FALSE = 'FALSE'

## Control flow.
IF = 'IF'

## Convenience variables.
binary_operators = binary_boolean_operators + binary_arithmetic_operators
unary_operators = unary_boolean_operators + unary_arithmetic_operators

## Types.
BOOLEAN = 'BOOLEAN'
NUMERIC = 'NUMERIC'
VALUE = 'VALUE'
NIL = 'NIL'


class AstError(Exception):
    """Error with the structure of the AST."""
    pass


def abs_to_disjunction(tree, abs_locs=None, recursive_call=False):
    """Given the abstract syntax tree (AST) `tree` of a numerical
    comparison/inequality predicate, and the list of locations in
    `tree` where absolute value forms appear, `abs_locs`, return the
    AST with no absolute value forms that represents the conjunction
    of disjunctions that is equivalent to `tree`.

    This should correctly handle strict and non-strict "greater than"
    and "less than" predicates, with absolute values on either side.
    It does *not* currently handle negated absolute value forms.

    """
    if not recursive_call:
        logger.debug('Top-level call to `abs_to_disjunction`.')
        assert abs_locs is None
    if abs_locs is None:
        abs_locs = find_absolute_value_locations(tree)
    n = len(abs_locs)
    if len(abs_locs) == 0:
        logger.debug('AST has no absolute values: {}'.format(tree))
        return tree

    logger.debug('AST with absolute values: {}'.format(tree))

    if tree[0] in ('<', '<='):
        lhs_test = lambda x: x[1] == 0
    elif tree[0] in ('>', '>='):
        lhs_test = lambda x: x[1] == 1
    elif tree[0] == '=':
        lhs_test = lambda x: False
    elif tree[0] == '<>':
        lhs_test = lambda x: True
    else:
        ## Not handling '=' or '<>' right now.
        assert False
    lhs_locs = []
    rhs_locs = []
    for loc in abs_locs:
        assert loc[0] == 1
        if lhs_test(loc):
            lhs_locs.append(loc)
        else:
            rhs_locs.append(loc)
    logger.debug('Left-hand-side absolute values at: {}'.format(lhs_locs))
    logger.debug('Right-hand-side absolute values at: {}'.format(rhs_locs))

    ## If any left-hand-side absolute values exist, then replace them;
    ## otherwise, replace the right-hand-side absolute values.
    if len(lhs_locs) > 0:
        n = len(lhs_locs)
        result_type = CONJUNCTION
        locations = lhs_locs
    else:
        n = len(rhs_locs)
        result_type = DISJUNCTION
        locations = rhs_locs
    assert n > 0
    patterns = list(itertools.product(*([[True, False]] * n)))

    transformed = []
    for pattern in patterns:
        variation = copy.deepcopy(tree)
        for i, p in enumerate(pattern):
            ## Warning/hack: modify the desired element of `variation`
            ## by reference here.
            element = variation
            for idx in locations[i][:-1]:
                element = element[idx]
            abs_form = element[locations[i][-1]]
            if p:
                ## Just take the argument of the absolute value (the
                ## "positive" version).
                abs_form[0] = 'POS'
            else:
                ## Negate the argument of the absolute value.
                abs_form[0] = NEG
        if result_type == CONJUNCTION:
            ## Make a recursive call to take care of the RHS.
            variation = abs_to_disjunction(
                variation, abs_locs=rhs_locs, recursive_call=True
            )
        else:
            pass
        transformed.append(variation)

    transformed = [result_type, transformed]
    logger.debug('Transformed AST: {}'.format(transformed))
    return transformed


def find_absolute_value_locations(tree, root=None):
    """Given the AST `tree`, return the list of (lists of) indices that
    correspond to absolute values.

    """
    if root is None:
        ## TODO: make sure this is a comparison.
        root = []
    if not isinstance(tree, (tuple, list)):
        return None
    elif len(tree) == 0:
        return None
    elif tree[0] == 'ABS':
        return [root]
    else:
        retval = []
        for idx, subtree in enumerate(tree):
            subroot = root + [idx]
            subretval = find_absolute_value_locations(subtree, root=subroot)
            if subretval is not None:
                retval += subretval
        return retval


def dump_ast(fname, parser, loaded_plugins=None):
    """Dump the AST of the file `fname` after parsing it with `parser`."""
    if loaded_plugins is None:
        loaded_plugins = []
    tree = parser.get_ast(fname)
    pprint.pprint(tree)
    ## Check for any plugins that do AST transformations, and apply
    ## them.
    for plugin in plugins.actions.get_active_plugins(
            loaded_plugins, plugins.actions.AST_TRANSORMATIONS
    ):
        transformer = plugin.Transformer()
        transformed = transformer.transform_ast(tree)
        tree = transformed
        logger.debug(
            'Applied AST transformations from the "{}" plugin.'
            .format(plugin.NAME)
        )
        print('### Transformed AST (via "{}" plugin): ###'.format(plugin.NAME))
        pprint.pprint(tree)


def write_ast(tree, directory=None):
    """Write the AST `tree` to a file in the specified `directory`."""
    if directory is None:
        pprint.pprint(tree)
    else:
        if not os.path.isdir(directory):
            os.mkdir(directory)
        path = directory + os.sep + 'ast.json'
        with open(path, 'w') as f:
            json.dump(tree, f)
            f.write('\n')
