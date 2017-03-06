# coding=utf-8
"""
malpy.actionrunner.ActionRunner Tests
"""
from __future__ import print_function

from nose.tools import assert_equal

import malpy.parser
import malpy.runner

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


PARSER = malpy.parser.Parser()
RUNNER = malpy.runner.Runner()


class TestMalActionRunner(object):
    """Tests the action runner class for consistency in the public facing API.

    """
    def test_reset(self):
        """validate reset works properly.

            Returns: None

        """
        test_program = PARSER.parse("MOVEI V63, R0\nEND\n")
        RUNNER.run(test_program, [0] * 64)
        assert_equal(RUNNER.registers[0], 63)
        RUNNER.reset()
        assert_equal(RUNNER.registers[0], 0)

    def test_run(self):
        """validate runner works proper with no JIT actions

            Returns: None

        """

        good_instrs = PARSER.parse(
                "LOAD R1, R0\n"
                "STORE R1, R0\n"
                "MOVE R1, R0\n"
                "ADD R2, R1, R0\n"
                "INC R2\n"
                "SUB R2, R1, R0\n"
                "DEC R2\n"
                "MOVEI V63, R1\n"
                "MUL R2, R1, R0\n"
                "DIV R2, R1, R0\n"
                "BLT R2, R1, L14\n"
                "BGT R2, R1, L14\n"
                "BEQ R2, R1, L14\n"
                "BR L3\n"
                "END\n "
        )
        mem = RUNNER.run(good_instrs, [0]*64)
        assert_equal(len(mem), 64)
        assert_equal(mem, [0]*64)

        bad_operands = ("MOVEI V63, V63\n"
                        "LOAD V63, V63\n"
                        "STORE V63, V63\n"
                        "MOVE V63, V63\n"
                        "ADD V63, V63, V63\n"
                        "INC V63\n"
                        "SUB V63, V63, V63\n"
                        "DEC V63\n"
                        "MUL V63, V63, V63\n"
                        "DIV V63, V63, V63\n"
                        "BLT V63, V63, V63\n"
                        "BGT V63, V63, V63\n"
                        "BEQ V63, V63, V63\n"
                        "BR V63").split('\n')

        for bad_instr in bad_operands:
            RUNNER.reset()
            prog = bad_instr+"\nEND\n"
            bad_ast = PARSER.parse(prog)
            print(prog, bad_ast)
            mem = RUNNER.run(bad_ast, [0]*64)
            assert_equal(len(mem), 3)
            assert_equal(mem, [False, False, True])

        out_of_bounds = PARSER.parse("BR L2\nEND\n")
        RUNNER.reset()
        mem = RUNNER.run(out_of_bounds, [0]*64)
        assert_equal(len(mem), 3)
        assert_equal(mem, [False, True, False])

        div_by_zero = PARSER.parse("DIV R2, R1, R0\nEND\n")
        RUNNER.reset()
        mem = RUNNER.run(div_by_zero, [0] * 64)
        assert_equal(len(mem), 3)
        assert_equal(mem, [True, False, False])

        bgt_works = PARSER.parse("MOVEI V63, R1\nBGT R1, R0, L2\nEND\n")
        RUNNER.reset()
        mem = RUNNER.run(bgt_works, [0] * 64)
        assert_equal(len(mem), 64)
        assert_equal(mem, [0]*64)

        blt_works = PARSER.parse("MOVEI V63, R0\nBLT R1, R0, L2\nEND\n")
        RUNNER.reset()
        mem = RUNNER.run(blt_works, [0] * 64)
        assert_equal(len(mem), 64)
        assert_equal(mem, [0]*64)

        beq_works = PARSER.parse("BEQ R1, R0, L1\nEND\n")
        RUNNER.reset()
        mem = RUNNER.run(beq_works, [0] * 64)
        assert_equal(len(mem), 64)
        assert_equal(mem, [0]*64)
