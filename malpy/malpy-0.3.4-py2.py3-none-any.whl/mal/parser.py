#!/usr/bin/env python
# coding=utf-8
"""
Mal assembler.
"""
import re
import collections


class Parser:
    """
    Implementation of a recursive descent parser.1
    Each method implement a single grammar rule.
    It walks from left to right over grammar rule.
    It will either consume the rule or generate a syntax error.
    """

    def __init__(self):
        self.Token = collections.namedtuple('Token', ['type', 'value'])
        self.scanner = re.Scanner([
            (r"\n|\r\n|\r", lambda scan, tok: self.Token('EOL', tok)),
            (r"V([0-5][0-9]|6[0-3])", lambda scan, tok: self.Token('VAL', tok)),
            (r"M([0-5][0-9]|6[0-3])", lambda scan, tok: self.Token('MEM', tok)),
            (r"R[0-9a-f]", lambda scan, tok: self.Token('REG', tok)),
            (r"L\d+", lambda scan, tok: self.Token('LABEL', tok)),
            (r",", lambda scan, tok: self.Token('COMMA', tok)),
            (r"[ \t]", lambda scan, tok: self.Token('WS', tok)),
            (r"MOVEI|LOAD|STORE|MOVE|ADD|INC|SUB|DEC|MUL|DIV|BEQ|BLT|BGT|BR|END",
             lambda scan, tok: self.Token('INSTR', tok))
        ])
        self.tokens = []
        self.current_token = None
        self.next_token = None

    def _generate_tokens(self, text):
        for token in self.scanner.scan(text)[0]:
            if token.type != 'WS':
                yield token

    def parse(self, text):
        """
        Parses a text string into a the MAL ast.
        :param text: The text to parse
        :return: A mult-level array representing the Assembly 'AST'
        """
        self.tokens = self._generate_tokens(text)
        self.current_token = None
        self.next_token = None
        self._advance()

        return self._program()

    def _advance(self):
        self.current_token, self.next_token = self.next_token, next(self.tokens,
                                                                    None)

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
        if not self._accept('EOL') and line:
            lines.append('ERR:001:Newline')
            return lines
        while self.next_token:
            line = self._instruction()
            lines.append(line)
            if not self._accept('EOL') and line:
                lines.append('ERR:001:Newline')
                break
        return lines

    def _instruction(self):
        operation_code = self._opcode()
        operands = []
        bad_operand = False
        if operation_code != 'END' and self.next_token:
            op = self._operand()
            if not op:
                bad_operand = True
            operands.append(op)
            while self._accept('COMMA'):
                op = self._operand()
                if not op:
                    bad_operand = True
                operands.append(op)

        if not operation_code:
            return 'ERR:003:Invalid mnemonic'
        if bad_operand:
            return 'ERR:004:Invalid operand type'

        if operation_code in ['END']:
            if len(operands) is 0:
                return [operation_code, operands]
            return 'ERR:002:Operand count'
        if operation_code in ['BR', 'INC', 'DEC']:
            if len(operands) is 1:
                return [operation_code, operands]
            return 'ERR:002:Operand count'
        if operation_code in ['MOVE', 'MOVEI', 'LOAD', 'STORE']:
            if len(operands) is 2:
                return [operation_code, operands]
            print(operands)
            return 'ERR:002:Operand count'
        if operation_code in ['ADD', 'SUB', 'MUL', 'DIV', 'BEQ', 'BLT', 'BGT']:
            if len(operands) is 3:
                return [operation_code, operands]
            return 'ERR:002:Operand count'
        return 'ERR:003:Invalid mnemonic'

    def _opcode(self):
        if self._accept('INSTR'):
            return self.current_token.value
        else:
            return None

    def _operand(self):
        if self._accept('REG') or self._accept('MEM') or \
                self._accept('LABEL') or self._accept('VAL'):
            return self.current_token.value
        return None

if __name__ == '__main__':
    import sys
    p = Parser()
    for arg in sys.argv[1:]:
        print(p.parse(open(arg).read()))
