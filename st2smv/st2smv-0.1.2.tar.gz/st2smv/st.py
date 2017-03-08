## Copyright (c) 2015-2016, Blake C. Rawlings.
##
## This file is part of `st2smv`.

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import sys
import time

import pyparsing as p

from . import ast
from . import utils

logger = utils.logging.getLogger(__name__)

## Increase the maximum recursion depth to parse deeply-nested
## expressions.
sys.setrecursionlimit(2000)

#############
# Operators #
#############

## Assignment.
COLEQ = p.Literal(':=').setParseAction(lambda x: ast.ASSIGN)

## Function block call arguments.
FBARG = p.Literal(':=').setParseAction(lambda x: ast.FBARG)
FBOUT = p.Literal('=>').setParseAction(lambda x: ast.FBOUT)

## Comparison.
LT = p.Literal('<').setParseAction(lambda x: ast.LT)
LEQ = p.Literal('<=').setParseAction(lambda x: ast.LEQ)
GT = p.Literal('>').setParseAction(lambda x: ast.GT)
GEQ = p.Literal('>=').setParseAction(lambda x: ast.GEQ)
NEQ = p.Literal('<>').setParseAction(lambda x: ast.NEQ)
EQ = p.Literal('=').setParseAction(lambda x: ast.EQ)
## Order is important here!  If it was 'LT | LEQ', then when matching
## an expression with '<=', this would match the '<' first, then hit
## the '=', and fail.
binop_comp = (NEQ | LEQ | LT | GEQ | GT | EQ)

## Boolean.
AND = p.CaselessKeyword('AND').setParseAction(lambda x: ast.AND)
OR = p.CaselessKeyword('OR').setParseAction(lambda x: ast.OR)
XOR = p.CaselessKeyword('XOR').setParseAction(lambda x: ast.XOR)
NOT = p.CaselessKeyword('NOT').setParseAction(lambda x: ast.NOT)
##
binop_bool = (AND | OR | XOR)
unop_bool = NOT

## Arithmetic.
ADD = p.Literal('+').setParseAction(lambda x: ast.ADD)
SUB = p.Literal('-').setParseAction(lambda x: ast.SUB)
MLT = p.Literal('*').setParseAction(lambda x: ast.MLT)
DIV = p.Literal('/').setParseAction(lambda x: ast.DIV)
EXP = p.Literal('**').setParseAction(lambda x: ast.EXP)
MOD = p.CaselessKeyword('MOD').setParseAction(lambda x: ast.MOD)
NEG = p.Literal('-').setParseAction(lambda x: ast.NEG)
##
binop_num = (EXP | MLT | SUB | ADD | DIV | MOD) # order: `EXP` before `MLT`
unop_num = NEG

## Convenience variables.
binop = (binop_comp | binop_bool | binop_num)
unop = (unop_bool | unop_num)

########################
# Symbols and Keywords #
########################

## Use .suppress() to prevent the symbol itself from showing up in the
## parsed output (e.g., if its meaning can be inferred from some other
## structure).
SEMICOLON = p.Literal(';').suppress()
COMMA = p.Literal(',').suppress()
LPAR = p.Literal('(').suppress()
RPAR = p.Literal(')').suppress()
TRUE = p.CaselessKeyword('TRUE').setParseAction(lambda x: ast.TRUE)
FALSE = p.CaselessKeyword('FALSE').setParseAction(lambda x: ast.FALSE)
IF = p.CaselessKeyword('IF').setParseAction(lambda x: ast.IF)
THEN = p.CaselessKeyword('THEN').suppress()
ELSIF = p.CaselessKeyword('ELSIF')
ELSE = p.CaselessKeyword('ELSE')
ENDIF = p.CaselessKeyword('END_IF').suppress()

##########
# Values #
##########

## Identifiers.
identifier = p.Word(p.alphas, p.alphanums + '_')
## Literals.
literal_bool = (TRUE | FALSE)
number_sequence = p.Word(p.nums)
literal_int = number_sequence
literal_real = p.Combine(
    (
        (p.Optional(number_sequence) + '.' + number_sequence)
        | (number_sequence + '.' + p.Optional(number_sequence))
    )
    + p.Optional(p.CaselessLiteral('E') + number_sequence)
)
literal_num = (literal_real | literal_int)
literal = (literal_bool | literal_num)
##
value = (literal | identifier)

############
# Comments #
############

comment_block = p.nestedExpr(opener='(*', closer='*)')
comment_line = p.Group('//' + p.restOfLine)
##
comment = (comment_block | comment_line)

###############
# Expressions #
###############

expression = p.Forward()
## Function calls.
grouping = p.Group(LPAR + expression + RPAR)
function_call = (
    identifier
    + LPAR
    + p.Optional(p.delimitedList(expression))
    + RPAR
)
function_call.setParseAction(
    lambda tokens: [[ast.CALL, [tokens[0], tokens[1:]]]]
)
## Function block calls.
_function_block_argument = (
    p.Group(identifier + FBARG + expression)
    | p.Group(identifier + FBOUT + identifier)
    | expression
)
function_block_call = (
    identifier
    + LPAR
    + p.Optional(p.delimitedList(_function_block_argument))
    + RPAR
)
function_block_call.setParseAction(
    lambda tokens: [[ast.FUNCTION_BLOCK_CALL, [tokens[0], tokens[1:]]]]
)
## Operator precedence via precedence levels (slow, lots of
## recursion!).
precedence_1 = p.Forward()
precedence_2 = p.Forward()
precedence_3 = p.Forward()
precedence_4 = p.Forward()
precedence_5 = p.Forward()
precedence_6 = p.Forward()
precedence_7 = p.Forward()
precedence_8 = p.Forward()
precedence_9 = p.Forward()
precedence_10 = p.Forward()
precedence_1 << (
    p.Group(precedence_2 + p.OneOrMore(OR + precedence_2))
    | precedence_2
)
precedence_2 << (
    p.Group(precedence_3 + p.OneOrMore(XOR + precedence_3))
    | precedence_3
)
precedence_3 << (
    p.Group(precedence_4 + p.OneOrMore(AND + precedence_4))
    | precedence_4
)
precedence_4 << (
    p.Group(precedence_5 + p.OneOrMore((EQ|NEQ) + precedence_5))
    | precedence_5
)
precedence_5 << (
    p.Group(precedence_6 + p.OneOrMore((LEQ|LT|GEQ|GT) + precedence_6))
    | precedence_6
)
precedence_6 << (
    p.Group(precedence_7 + p.OneOrMore((ADD|SUB) + precedence_7))
    | precedence_7
)
precedence_7 << (
    p.Group(precedence_8 + p.OneOrMore((MLT|DIV|MOD) + precedence_8))
    | precedence_8
)
precedence_8 << (
    p.Group((NEG|NOT) + precedence_8)
    | precedence_9
)
precedence_9 << (
    p.Group(precedence_10 + p.OneOrMore(EXP + precedence_10))
    | precedence_10
)
precedence_10 << (grouping | function_call | function_block_call | value)
## (Not used currently) operator precedence via a built-in `pyparsing`
## method (/incredibly/ slow without `.enablePackrat()`).
operation = p.infixNotation(
    (function_call | function_block_call | value),
    [
        (EXP, 2, p.opAssoc.LEFT),
        ((NEG|NOT), 1, p.opAssoc.RIGHT),
        ((MLT|DIV|MOD), 2, p.opAssoc.LEFT),
        ((ADD|SUB), 2, p.opAssoc.LEFT),
        ((LEQ|LT|GEQ|GT), 2, p.opAssoc.LEFT),
        ((EQ|NEQ), 2, p.opAssoc.LEFT),
        (AND, 2, p.opAssoc.LEFT),
        (XOR, 2, p.opAssoc.LEFT),
        (OR, 2, p.opAssoc.LEFT),
    ]
)
operation.enablePackrat()
##
expression << precedence_1

################
# Instructions #
################

instruction = p.Group((function_call | function_block_call) + SEMICOLON)

##############
# Statements #
##############

statement = p.Forward()
## Assignments.
assignment = (
    identifier + COLEQ + expression + SEMICOLON
)
## IF/ELSIF/ELSE.
elsif_block = (
    ELSIF + expression + THEN +
    p.Group(p.ZeroOrMore(statement))
)
else_block = (
    ELSE +
    p.Group(p.ZeroOrMore(statement))
)
if_elsif_else = (
    IF + expression + THEN +
    p.Group(p.ZeroOrMore(statement)) +
    p.Optional(p.OneOrMore(elsif_block)) +
    p.Optional(else_block) +
    ENDIF + SEMICOLON
)
##
statement << p.Group(
    if_elsif_else
    | assignment
    | instruction
)

###################
# String Literals #
###################

quoted_string = p.QuotedString('"', multiline=True)

###############
# Blank Lines #
###############

blank_line = SEMICOLON

#################
# The Main Loop #
#################

main_loop = p.OneOrMore(
    statement | quoted_string.suppress() | blank_line.suppress()
)
main_loop.ignore(comment)


@utils.timing(log_fun=logger.info, log_text='Parsed the ST file: {:.2f}s')
def _parse(path):
    """Parse the Structured Text file located at `path`."""
    with open(path) as f:
        lines = f.readlines()
    n_lines = len(lines)
    step_size = 1
    out = None
    fromline = 0
    toline = min(fromline + step_size, n_lines)
    while True:
        if fromline >= n_lines:
            ## Done parsing.  Strict inequality should never hold.
            break
        logger.debug(
            'Parsing lines {}-{} ({} lines) of {}'
            .format(fromline+1, toline, toline - fromline, n_lines)
        )
        working = '\n'.join(lines[fromline : toline])
        try:
            ## Parse and record.
            chunk = main_loop.parseString(working, parseAll=True)
            if out is None:
                out = chunk
            else:
                out += chunk
            ## Update for the next iteration.
            fromline = min(toline, n_lines)
            toline = min(fromline + step_size, n_lines)
        except p.ParseException:
            if toline == n_lines:
                ## Failed.
                break
            toline = min(toline + 1, n_lines)
            continue
    if fromline < n_lines:
        logger.warning(
            'Did not completely parse the file; failed after line {}'
            .format(fromline+1)
        )
    return out


def parse_symbol(s, expr_type):
    """Try to parse a single symbol of structured text code as a
    particular type of expression.

    """
    s = str(s)
    try:
        out = expr_type.parseString(s)[0]
    except p.ParseException:
        out = None
    return out


def pt_to_ast(tree):
    """Convert the parse tree to an abstract syntax tree (AST)."""
    ## Do some simple preprocessing.
    assert isinstance(tree, (p.ParseResults, list, utils.six.string_types))
    ##
    if isinstance(tree, (str, utils.six.string_types)):
        ## Base case, got to a symbol.
        return tree
    elif len(tree) == 0:
        return tree
    elif len(tree) == 1:
        ## A node with a single child, replace node with child.
        return pt_to_ast(tree[0])
    elif tree[0] in ast.unary_operators:
        ## Unary operator.
        assert len(tree) == 2
        return [tree[0], pt_to_ast(tree[1])]
    elif tree[0] == ast.IF:
        ## IF statement.
        assert len(tree) >= 3
        ## Check for ELSIF, replace with ELSE IF
        if ELSIF in tree[1:]:
            assert len(tree) >= 6
            assert tree[3] == parse_symbol(tree[3], ELSIF)
            return [
                tree[0],
                [
                    pt_to_ast(tree[1]),
                    pt_to_ast(tree[2]),
                    pt_to_ast([ast.IF] + tree[4:]),
                ],
            ]
        elif ELSE in tree[1:]:
            ## IF-ELSE statement.
            return [
                tree[0],
                [
                    pt_to_ast(tree[1]),
                    pt_to_ast(tree[2:-2]),
                    pt_to_ast(tree[-1]),
                ],
            ]
        else:
            ## Simple IF statement.
            assert len(tree) == 3
            return [
                tree[0],
                [
                    pt_to_ast(tree[1]),
                    pt_to_ast(tree[2]),
                    [],
                ],
            ]
    elif tree[0] in (ast.CALL, ast.FUNCTION_BLOCK_CALL):
        assert len(tree) == 2
        assert len(tree[1]) == 2
        return [tree[0], [tree[1][0], [pt_to_ast(x) for x in tree[1][1]]]]
    elif tree[1] == ast.ASSIGN:
        ## Assignment.
        assert len(tree) == 3
        return [tree[1], [pt_to_ast(tree[0]), pt_to_ast(tree[2])]]
    elif tree[1] in ast.function_block_operators:
        ## Function block argument "declaration".
        return [tree[1], [pt_to_ast(tree[0]), pt_to_ast(tree[2])]]
    elif tree[1] in (ast.binary_operators + ast.comparators):
        ## Binary operator.
        n = len(tree)
        assert n >= 3 and (n - 3) % 2 == 0
        if True:
            ## Left-associative.
            head = tree[0:-2]
            operator = tree[-2]
            assert operator in (ast.binary_operators + ast.comparators)
            tail = tree[-1]
        else:
            ## Right-associative.
            head = tree[0]
            operator = tree[1]
            tail = tree[2:]
        return [operator, [pt_to_ast(head), pt_to_ast(tail)]]
    else:
        ## Descend.
        return [pt_to_ast(x) for x in tree]


def get_ast(path):
    parse_tree = _parse(path)
    t0 = time.time()
    abstract_syntax_tree = pt_to_ast(parse_tree)
    t1 = time.time()
    logger.info('Created AST: {0:.2f}s'.format(t1 - t0))
    return abstract_syntax_tree
