## Copyright (c) 2016, Blake C. Rawlings.
##
## This file is part of `st2smv`.

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from ... import ast
from ... import ir
from ... import plugins
from ... import utils

logger = utils.logging.getLogger(__name__)

## Plugin information.
NAME = 'stdlib'
ACTIONS = (
    plugins.actions.SPECIAL_EXPRESSIONS,
    plugins.actions.UNTOUCHABLE,
)
OPTIONS = {}

DT = 'DT'
SPECIAL_EXPRESSION_TYPES = (DT,)


def convert_expression(converter, tree, lhs=False):
    """Convert the AST `tree` that corresponds to an expression.

    This modifies `self` and returns the converted expression.

    """
    assert tree[0] in SPECIAL_EXPRESSION_TYPES
    if tree[0] == 'DT':
        assert lhs is False
        return _convert_delay_timer(converter, tree)
    else:
        raise ir.ConversionError(
            'Unrecognized expression: {0}'.format(tree)
        )


def _convert_delay_timer(converter, tree):
    """Convert a call to `DT(reading, duration, default)` (a delay timer).

     This modifies `self`.

    """
    assert len(tree) == 2
    assert len(tree[1]) == 3
    assert tree[0] == 'DT'
    ## Check usage.
    if converter.if_depth > 0:
        raise ir.ConversionError(
            'Unsupported input code: DT inside IF...ELSE'
        )
    ## Handle the arguments to the `DT` function call; `duration`
    ## is ignored.
    reading = converter.convert_expression(tree[1][0])
    default = converter.convert_expression(tree[1][2])
    converter.set_type(reading, ast.BOOLEAN)
    ## Create the variable that will represent the timer.
    timer_variable = converter.convert_expression('dt', lhs=True)
    converter.assigned.remove(ir.Var('dt', None)) # only `dt.value` is assigned
    timer_value = ir.Var(
        timer_variable.label, timer_variable.version,
        field='value',
    )
    converter.referenced.add(timer_value)
    converter.defined.add(timer_value)
    _mark_timer(converter, timer_variable, timer_value)
    converter.set_type(timer_value, ast.BOOLEAN)
    ## Save the intermediate representation.
    converter.logic_ir.append(
        ['VAR', timer_variable, ['delay_timer', reading, default]]
    )
    ## Mark the connections.
    reading_symbols = ir.get_variables(reading)
    variables = set.union(converter.defined, converter.referenced)
    reading_vars = {x for x in variables if x in reading_symbols}
    for rvar in reading_vars:
        converter.mark_connection(timer_value, rvar)
    ## Return the expression that holds the timer's value.
    return timer_value


def _mark_timer(converter, timer, timer_value):
    if 'timers' not in converter.special_variables:
        converter.special_variables['timers'] = set()
    if 'timer_values' not in converter.special_variables:
        converter.special_variables['timer_values'] = set()
    converter.special_variables['timers'].add(timer)
    converter.special_variables['timer_values'].add(timer_value)


def is_untouchable(converter, variable):
    """Return whether or not `variable` is "untouchable".

    A variable is "untouchable" if it cannot (or should not) be
    abstracted away when simplifying the model.

    """
    timers = converter.special_variables.get('timers', set())
    timer_values = converter.special_variables.get('timer_values', set())
    if variable in (timers | timer_values):
        return True
    else:
        return False
