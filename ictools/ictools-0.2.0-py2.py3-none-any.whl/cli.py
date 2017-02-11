import argparse
import logging
import os
import sys

from ictools import version


class IncreaseVerbosity(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        steps = [logging.CRITICAL, logging.ERROR, logging.WARNING,
                 logging.INFO, logging.DEBUG]

        root = logging.getLogger()
        if root.level == logging.NOTSET:
            root.setLevel(logging.CRITICAL)
        else:
            for step in steps:
                if root.level > step:
                    root.setLevel(step)
                    break


class SilenceLogging(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        logging.getLogger().handlers = [logging.NullHandler()]


def configure_logging():
    logging.basicConfig(level=logging.WARNING, stream=sys.stderr,
                        format='%(levelname)1.1s - %(name)s: %(message)s')


def get_parent_parsers():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--quiet', '-q', action=SilenceLogging, nargs=0,
                        help='disable diagnostic output')
    parser.add_argument('--version', action='version', version=version)
    parser.add_argument('--verbose', '-v', action=IncreaseVerbosity, nargs=0,
                        help='increase diagnostic verbosity')
    return [parser]


def require_environment(logger, var_name):
    try:
        return os.environ[var_name]
    except KeyError as exc:
        logger.error('%s is a required environment variable', var_name)
        sys.exit(os.EX_USAGE)
