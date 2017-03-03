# coding=utf-8
"""
malpy.parser.Parser Tests
"""
from __future__ import print_function
from nose.tools import assert_equal

import malpy.parser
from malpy.parser import Token

PARSER = malpy.parser.Parser()

operand_counts = {
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


class TestMalParser(object):
    """
    Tests the parser class for consistency in public facing API.
    """
    @classmethod
    def setup_class(cls):
        """
        Creates the parser to use for testing.
        :return: None
        """

    def test_generate_tokens(self):
        """
        Makes sure token generator yields proper tokens.
        :return: None
        """

        ##
        # Empty Text
        ##
        test_empty = PARSER.generate_tokens('')
        assert_equal(list(test_empty), [])

        ##
        # EOL Tokens
        ##
        test_eol_unix = PARSER.generate_tokens('\n')
        assert_equal(list(test_eol_unix), [Token('EOL', '\n')])

        test_eol_mac = PARSER.generate_tokens('\r')
        assert_equal(list(test_eol_mac), [Token('EOL', '\r')])

        test_eol_win = PARSER.generate_tokens('\r\n')
        assert_equal(list(test_eol_win), [Token('EOL', '\r\n')])

        ##
        # VAL Tokens
        ##
        for i in range(64):
            val = "V{0:02d}".format(i)
            test_val = PARSER.generate_tokens(val)
            assert_equal(list(test_val), [Token('VAL', val)])

        ##
        # MEM Tokens
        ##
        for i in range(64):
            mem = "M{0:02d}".format(i)
            test_mem = PARSER.generate_tokens(mem)
            assert_equal(list(test_mem), [Token('MEM', mem)])

        ##
        # REG Tokens
        ##
        for i in range(10):
            reg = "R{0:x}".format(i)
            test_reg = PARSER.generate_tokens(reg)
            assert_equal(list(test_reg), [Token('REG', reg)])

        for i in range(10, 16):
            good_reg = "R{0:x}".format(i)
            bad_reg = "R{0:X}".format(i)  # Don't match uppercase hex A-F
            test_reg = PARSER.generate_tokens(good_reg+bad_reg)
            assert_equal(list(test_reg), [Token('REG', good_reg),
                                          Token('NTYPE', 'NOP')])

        ##
        # LABEL Tokens
        ##
        for i in range(10, 60):
            label = "L{0:d}".format(i)
            test_label = PARSER.generate_tokens(label)
            assert_equal(list(test_label), [Token('LABEL', label)])

        ##
        # COMMA and WS Tokens
        ##
        test_comma = PARSER.generate_tokens(',')
        assert_equal(list(test_comma), [Token('COMMA', ',')])

        test_ws = PARSER.generate_tokens('\t ')
        assert_equal(list(test_ws), [])

        ##
        # INSTR Tokens and order preservation
        ##
        instrs = "MOVEI LOAD STORE MOVE ADD INC SUB DEC MUL DIV BEQ " \
                 "BLT BGT BR END"
        test_instr = PARSER.generate_tokens(instrs)
        assert_equal(list(test_instr), [Token('INSTR', instr)
                                        for instr in instrs.split()])

    def test_parse(self):
        """
        Makes sure the parser creates proper errors and AST's.
        :return: None
        """
        test_err001 = PARSER.parse("MOVEI Ra, V63")
        assert_equal(test_err001, ['ERR:001:Newline'])

        test_err002 = PARSER.parse("MOVEI Ra\n")
        assert_equal(test_err002, ['ERR:002:Invalid operand count'])

        test_err003 = PARSER.parse("NOT_HERE\n")
        assert_equal(test_err003, ['ERR:003:Invalid mnemonic'])

        test_err004 = PARSER.parse("MOVEI R0, NOT_HERE\n")
        assert_equal(test_err004, ['ERR:004:Invalid operand'])

        instrs = "MOVEI LOAD STORE MOVE ADD INC SUB DEC MUL DIV BEQ " \
                 "BLT BGT BR END"
        prog = ""

        output = []

        for instr in instrs.split():
            prog += instr+(" R0,"*operand_counts.get(instr, 0))[:-1]+"\n"
            output.append([instr, ("R0 "*operand_counts.get(instr, 0))[:-1]
                          .split()])
        print(prog)
        test_all_valid = PARSER.parse(prog)
        assert_equal(test_all_valid, output)
