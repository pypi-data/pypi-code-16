import argparse


class CommandLineArgumentParser:
    PROGRAM = 'files-by-date'

    DESCRIPTION = """
    Files-By-Date v1.1:
    A Python program that takes files within an input directory and copies them\n
    to a target directory, sorted into [YYYYMM] format subdirectories based\n
    upon the file create date.
    """

    def __init__(self):
        self.argument_parser = argparse.ArgumentParser(prog=CommandLineArgumentParser.PROGRAM,
                                                       description=CommandLineArgumentParser.DESCRIPTION)
        self._add_arguments()

    def parse(self, *, args=None):
        return self.argument_parser.parse_args(args=args)

    def print_help(self):
        self.argument_parser.print_help()

    def _add_arguments(self):
        parser = argparse.ArgumentParser(description='Process some integers.')
        self.argument_parser.add_argument("input_dir", type=str, help="input directory")
        self.argument_parser.add_argument("target_dir", type=str, help="target output directory")
        self.argument_parser.add_argument("-f", type=bool, default=False,
                                          help="Force overwrite of files in target directory", dest='force_overwrite')
