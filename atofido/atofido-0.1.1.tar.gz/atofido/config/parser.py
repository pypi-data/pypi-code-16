# -*- coding: utf-8 -*-

import argparse


class Parser(object):
    def __init__(self):
        self._parser = argparse.ArgumentParser(description='Automatic TOrrent FIles DOwnloader. ')
        self._parser.add_argument('-v', '--version', action='version', version="0.0.1",
                                  help="returns autosubmit's version number and exit")

        subparsers = self._parser.add_subparsers(dest='command')

        subparser = subparsers.add_parser('list', description='list all the matching available torrents')
        subparser.add_argument('name', help='torrent identifier')

        subparser = subparsers.add_parser('download', description='downloads the given torrent')
        subparser.add_argument('name', help='torrent identifier')

    def parse_args(self, args):
        args = self._parser.parse_args(args)
        return args.command, args
