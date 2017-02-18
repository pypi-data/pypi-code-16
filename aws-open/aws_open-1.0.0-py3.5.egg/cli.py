#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from argparse import ArgumentParser
from .sg_open import sg_open
from .sg_close import sg_close
from .sg_list import print_open_sgs, print_closed_sgs

def create_parser():
      parser = ArgumentParser()
      subparsers = parser.add_subparsers(dest='command')
      p_open = subparsers.add_parser('open', help='Add rules to open SSH to the local IP')
      open_group = p_open.add_mutually_exclusive_group(required=True)
      open_group.add_argument('--name', dest='name', help='Name of a Securiy Group to which to add the SSH rule')
      open_group.add_argument('-a', '--all', action='store_true', help='If set, will add the SSH rule to all existing Security Groups')

      p_close = subparsers.add_parser('close', help='Removes rules allowing SSH access to the local IP')
      close_group = p_close.add_mutually_exclusive_group(required=True)
      close_group.add_argument('--name', dest='name', help='Name of a Securiy Group from which to remove the SSH rules')
      close_group.add_argument('-a', '--all', action='store_true', help='If set, will try to remove all SSH rules from a given SG, or all SSH rules specific to the local IP, otherwise')

      subparsers.add_parser('list-open', help='Lists Security Groups that have SSH rules allowing access from this IP')
      subparsers.add_parser('list-closed', help='Lists Security Groups that do not have SSH rules allowing access from this IP')

      return parser


def main():
      parser = create_parser()
      if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(0)

      args = parser.parse_args()
      if args.command == 'close':
            sg_close(sg_name=args.name, all_sgs=args.all)
      elif args.command == 'open':
            sg_open(sg_name=args.name, all_sgs=args.all)
      elif args.command == 'list-open':
            print_open_sgs()
      elif args.command == 'list-closed':
            print_closed_sgs()


if __name__ == "__main__":
      main()
