# coding=utf-8
"""
malpy.actionrunner.ActionRunner Tests
"""
from __future__ import print_function
from nose.tools import assert_equal

import malpy.actionrunner
import malpy.parser

PARSER = malpy.parser.Parser()
RUNNER = malpy.actionrunner.ActionRunner(dict([]))


class TestMalActionRunner(object):
    """
    Tests the action runner class for consistency in the public facing API.
    """
    def setup(self):
        """
        Resets the memory, registers and program counter before each test.
        :return: None
        """
        RUNNER.reset()

    def test_reset(self):
        """
        validate reset works properly.
        :return: None
        """
        test_program = PARSER.parse("MOVEI V63, R0\nEND\n")
        RUNNER.run(test_program, [0 for _ in range(64)])
        assert_equal(RUNNER.registers[0], 63)
        RUNNER.reset()
        assert_equal(RUNNER.registers[0], 0)
