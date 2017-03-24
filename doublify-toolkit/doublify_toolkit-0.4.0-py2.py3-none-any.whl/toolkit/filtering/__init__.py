import re
from enum import Enum
from typing import Iterable

from . import filtering_pb2

_TOKEN_SPECIFICATION = re.Scanner([
    (r'".+?"', lambda _, t: (Token.STRING, t)),
    (r'[0-9]*(\.?[0-9]+)+', lambda _, t: (Token.NUMERIC, t)),
    (r'\w+', lambda _, t: (Token.IDENTIFIER, t)),
    (r'\{|\}', lambda _, t: (Token.PARENTHESES, t)),
    (r'\(|\)', lambda _, t: (Token.CURLY, t)),
    (r'\:', lambda _, t: (Token.COLON, t)),
    (r'[ \t]+', None),
])


class Token(Enum):
    """
    Token type represent.
    """
    STRING = 1

    NUMERIC = 2

    IDENTIFIER = 3

    PARENTHESES = 4

    CURLY = 5

    COLON = 6


def tokenize(query: str) -> Iterable[tuple]:
    """
    :param query: Raw DQL query.
    :return: List tokens.
    :rtype Iterable[tuple]
    """
    reply, _ = _TOKEN_SPECIFICATION.scan(query)
    return reply


def parse_query(query: str) -> filtering_pb2.Query:
    """
    :param query: Raw DQL query.
    :return: DQL Query.
    :rtype filtering_pb2.Query
    """

    reply = tokenize(query)

    named_bindings = dict()

    current_binding = filtering_pb2.Filter()

    current_name = None

    kind_rep = dict()

    for token, kind in reply:
        if token == Token.IDENTIFIER:
            if kind in ('true', 'false', ):
                kind_rep = dict(bool_value=kind == 'true')
            elif kind in ('is', 'not'):
                kind_rep = dict(bool_value=kind == 'is')
            else:
                current_name = kind
        elif token == Token.STRING:
            kind_rep = dict(string_value=kind.strip('"'))
        elif token == Token.NUMERIC:
            if '.' in kind:
                kind_rep = dict(float_value=float(kind))
            else:
                kind_rep = dict(number_value=int(kind))
        elif token == Token.PARENTHESES and kind == '{':
            current_binding.operation = 2
        elif token == Token.CURLY and kind == '(':
            current_binding.operation = 3

        if current_binding.operation >= 2 and kind in ('}', ')', ):
            named_bindings[current_name] = current_binding

            current_binding = filtering_pb2.Filter()
            current_name = None
        elif current_binding.operation >= 2 and kind_rep:
            current_binding.value.array_values.values.add(**kind_rep)

            kind_rep = dict()
        elif current_binding.operation <= 1 and kind_rep and current_name:
            current_binding.operation = 1

            for k in kind_rep:
                setattr(current_binding.value, k, kind_rep[k])

            named_bindings[current_name] = current_binding

            current_binding = filtering_pb2.Filter()
            current_name = None

            kind_rep = dict()

    return filtering_pb2.Query(named_bindings=named_bindings)
