import argparse
from unittest import TestCase

import pytest

from files_by_date.parsers.command_line_argument_parser import CommandLineArgumentParser


class TestCommandLineArgumentParser(TestCase):
    def test_command_line_argument_parser(self):
        command_line_argument_parser = CommandLineArgumentParser()

        assert command_line_argument_parser.argument_parser
        assert isinstance(command_line_argument_parser.argument_parser, argparse.ArgumentParser)

        assert command_line_argument_parser.argument_parser.description == CommandLineArgumentParser.DESCRIPTION
        assert command_line_argument_parser.argument_parser.prog == CommandLineArgumentParser.PROGRAM

        with pytest.raises(BaseException):
            command_line_argument_parser.parse(args=[])
        with pytest.raises(BaseException):
            command_line_argument_parser.parse()

        arguments = command_line_argument_parser.parse(args='input_dir target_dir'.split())
        assert arguments.input_dir == 'input_dir'
        assert arguments.target_dir == 'target_dir'
        assert not arguments.force_overwrite

        arguments = command_line_argument_parser.parse(args='input_dir target_dir -f true'.split())
        assert arguments.force_overwrite
