"""pocli -- command line interface

Copyright (c) 2016, 2017
Florian Kaiser (fek@rzg.mpg.de), Klaus Reuter (khr@rzg.mpg.de)
"""


import os
from . import lib


def parse_args():
    import argparse
    from . import lib
    # ---
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='Commands')
    # ---
    parser_put = subparsers.add_parser(
        'put', help='upload file(s)')
    # parser_put.add_argument('--input', type=str, help='input parameter file')
    parser_put.set_defaults(func=lib.put)
    parser_put.add_argument('--directory', '-d', type=str, help='remote directory')
    parser_put.add_argument('files', nargs=argparse.REMAINDER, help='local file(s)')
    # ---
    parser_get = subparsers.add_parser(
        'get', help='download file(s)')
    parser_get.set_defaults(func=lib.get)
    parser_get.add_argument('--directory', '-d', type=str, help='local directory')
    parser_get.add_argument('files', nargs=argparse.REMAINDER, help='remote file(s)')
    # ---
    parser_ls = subparsers.add_parser(
        'ls', help='list remote directory')
    parser_ls.set_defaults(func=lib.ls)
    parser_ls.add_argument('dir', nargs=argparse.REMAINDER, help='remote directory')
    # ---
    parser_rm = subparsers.add_parser(
        'rm', help='delete remote object')
    parser_rm.set_defaults(func=lib.rm)
    parser_rm.add_argument('file', nargs=argparse.REMAINDER, help='remote file')
    # ---
    parser_mkdir = subparsers.add_parser(
        'mkdir', help='create remote directory')
    parser_mkdir.set_defaults(func=lib.mkdir)
    parser_mkdir.add_argument('dir', nargs=argparse.REMAINDER, help='remote directory')
    # ---
    parser_check = subparsers.add_parser(
        'check', help='check current configuration')
    parser_check.set_defaults(func=lib.check)
    # ---
    return parser.parse_args()


def main():
    if not os.path.isfile( lib.get_ocrc() ):
        lib.init_ocrc()
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
