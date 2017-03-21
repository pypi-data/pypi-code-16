# -*- coding: utf-8 -*-

import argparse
import logging.config
import os
import sys

from .utils import build, init
from .server import server


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': ('[%(levelname)1.1s %(asctime)s '
                       '%(name)s] '
                       '%(message)s')
        },
        'simple': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'app': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'wt': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'wt.app': {
            'handlers': ['app'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'wt.init': {
            'handlers': ['app'],
            'level': 'INFO',
            'propagate': False,
        },
        'aiohttp': {
            'handlers': ['app'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}
logging.config.dictConfig(LOGGING)


def abspath(fn):  # pragma: no cover
    return os.path.abspath(os.path.expanduser(fn))


class AbsPathFileAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, abspath(values))


def parse_args(args):

    parser = argparse.ArgumentParser(
        description='Command-line interface to static site generator')
    parser.add_argument(
        '-c', '--conf',
        default=abspath('wt.yaml'),
        dest='config',
        metavar='wt.yaml',
        action=AbsPathFileAction,
        help='configuration file (defaults to wt.yaml in current directory)')

    subparsers = parser.add_subparsers(
        title='commands',
        dest='command')

    init_cmd = subparsers.add_parser('init',
                                     help='bootstrap project structure')
    init_cmd.add_argument(dest='path',
                          action=AbsPathFileAction,
                          help='path to folder to bootstrap in')

    develop_cmd = subparsers.add_parser(
        'develop',
        help='start simple http server for development')
    develop_cmd.add_argument(
        '--host',
        default='127.0.0.1',
        dest='host',
        help='address to run server at (defaults to 127.0.0.1)')
    develop_cmd.add_argument(
        '--port',
        default=9000,
        type=int,
        dest='port',
        help='port to bind server to (defaults to 9000)')

    subparsers.add_parser('build', help='build site')

    return parser.parse_args(args)


def main():  # pragma: no cover
    ret = 1
    args = parse_args(sys.argv[1:])
    if args.command == 'develop':
        ret = server(args.config, args.host, args.port)
    elif args.command == 'build':
        ret = build(args.config)
    elif args.command == 'init':
        ret = init(args.path)
    sys.exit(ret)
