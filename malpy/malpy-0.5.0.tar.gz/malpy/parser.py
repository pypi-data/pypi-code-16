# coding=utf-8
"""Mal assembler.

"""
import collections
import re

Token = collections.namedtuple('Token', ['type', 'value'])


class Parser(object):
    """Implementation of a recursive descent parser.

    Each method implement a single grammar rule.
    It walks from left to right over grammar rule.
    It will either consume the rule or generate a syntax error.

    """

    def __init__(self):
        self.scanner = re.Scanner([
            (r"\n|\r\n|\r", lambda _, tok: Token('EOL', tok)),
            (r"V([0-5][0-9]|6[0-3])", lambda _, tok: Token('VAL', tok)),
            (r"M([0-5][0-9]|6[0-3])", lambda _, tok: Token('MEM', tok)),
            (r"R[0-9a-f]", lambda _, tok: Token('REG', tok)),
            (r"L\d+", lambda _, tok: Token('LABEL', tok)),
            (r",", lambda _, tok: Token('COMMA', tok)),
            (r"[ \t]", lambda _, tok: Token('WS', tok)),
            (r"MOVEI|LOAD|STORE|MOVE|ADD|INC|SUB|DEC|MUL|DIV|BEQ|BLT|BGT"
             r"|BR|END",
             lambda _, tok: Token('INSTR', tok)),
            (r".+", lambda _, tok: Token('NTYPE', 'NOP'))
        ])
        self.tokens = []
        self.current_token = None
        self.next_token = None
        self.operand_counts = {
            'END': 0,
            'BR': 1,
            'INC': 1,
            'DEC': 1,
            'MOVE': 2,
            'MOVEI': 2,
            'LOAD': 2,
            'STORE': 2,
            'ADD': 3,
            'SUB': 3,
            'MUL': 3,
            'DIV': 3,
            'BEQ': 3,
            'BLT': 3,
            'BGT': 3
        }

    def generate_tokens(self, text):
        """String-to-token generator.

        Args:
            text (str): Input string of lines that are newline delimited

        Returns:
            list[Token]: a generated token list.

        """
        for token in self.scanner.scan(text)[0]:
            if token.type != 'WS':
                yield token

    def parse(self, text):
        """Parses a text string into a the MAL ast.

        Args:
            text: The text to parse

        Returns:
             list[list[str, list[str]]]: An array representing the 'AST'.

        """
        self.tokens = self.generate_tokens(text)
        self.current_token = None
        self.next_token = None
        self._advance()

        return self._program()

    def _advance(self):
        self.current_token = self.next_token
        self.next_token = next(self.tokens, None)

    def _eat_to_eol(self):
        while self.current_token and not self._accept('EOL'):
            self._advance()

    def _accept(self, token_type):
        # if there is next token and token type matches
        if self.next_token and self.next_token.type == token_type:
            self._advance()
            return True
        else:
            return False

    def _program(self):
        lines = []
        line = self._instruction()
        lines.append(line)
        # Don't replace other errors or valid lines
        if not self._accept('EOL') and line and line[0] != 'E':
            lines[-1] = 'ERR:001:Newline'
            self._eat_to_eol()
        while self.current_token and self.next_token:
            line = self._instruction()
            lines.append(line)
            # Don't replace other errors or valid lines
            if not self._accept('EOL')\
                    and line and line[0] != 'E':
                lines[-1] = 'ERR:001:Newline'
                self._eat_to_eol()
        return lines

    def _instruction(self):
        operation_code = self._opcode()
        if not operation_code:
            self._eat_to_eol()
            return 'ERR:003:Invalid mnemonic'

        operands = []
        bad_operand = False
        operand = self._operand()
        if operation_code != 'END' and not operand:
            bad_operand = True
        if operand:
            operands.append(operand)
        while self._accept('COMMA'):
            operand = self._operand()
            if not operand:
                bad_operand = True
            operands.append(operand)

        if bad_operand:
            self._eat_to_eol()
            return 'ERR:004:Invalid operand'

        if operation_code in self.operand_counts:
            if len(operands) == self.operand_counts[operation_code]:
                return [operation_code, operands]
            return 'ERR:002:Invalid operand count'
        # return 'ERR:003:Invalid mnemonic' # Unreachable

    def _opcode(self):
        if self._accept('INSTR'):
            return self.current_token.value
        else:
            return None

    def _operand(self):
        if (self._accept('REG') or self._accept('MEM') or
                self._accept('LABEL') or self._accept('VAL')):
            return self.current_token.value
        return None
