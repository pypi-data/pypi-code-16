"""Script to verify installed packages match pip requirement files."""

import argparse
import pkg_resources

from verifyreq import version


def get_args(args=None):
    """Process command line arguments."""
    parser = argparse.ArgumentParser(
        description='Package installation verifier')
    parser.add_argument(
        '--version', action='version', version=version.__version__)
    parser.add_argument(
        'requirement', help='pip requirement file to verify against',
        type=argparse.FileType('rt'), nargs='+')
    return parser.parse_args(args=args)


def main():
    """Get args and run verifier."""
    args = get_args()
    verify_requirements(args.requirement)


def verify_requirements(requirement_files):
    """Check a sequence of requirement files for consistency."""
    for reqfile in requirement_files:
        print('Checking ' + reqfile.name)
        reqs = reqfile.readlines()
        pkg_resources.require(reqs)
