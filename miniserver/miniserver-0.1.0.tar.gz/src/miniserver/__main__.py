import argparse
import sys

from miniserver import __version__
from miniserver.runners import load_miniserver_app_from_file


def get_parser():
    """
    Creates a new argument parser.
    """
    parser = argparse.ArgumentParser('miniserver')
    version = '%(prog)s ' + __version__
    parser.add_argument('--version', '-v', action='version', version=version)
    return parser


def main(argv=None):
    """
    Main script for miniserver.
    """

    parser = get_parser()
    if argv is None:
        argv = sys.argv

    if len(argv) == 1:
        parser.parse_args(['-h'])
    elif argv[1].endswith('.py'):
        try:
            load_miniserver_app_from_file(argv[1])
        except FileNotFoundError:
            raise SystemError('file not found: %s' % argv[0])
    else:
        parser.parse_args(argv)

if __name__ == '__main__':
    main()