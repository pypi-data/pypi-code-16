#!/usr/bin/env python3

from statically.logic import logic
import argparse


def parse_args():

    """parse command line arguments"""

    parser = argparse.ArgumentParser(description="Static site generator with markdown.")
    parser.add_argument("command", type=str,
                        help="Command to perform: init, update.")
    parser.add_argument("path", type=str, help="Statically instance directory.")

    return parser.parse_args()


def main(args):
    statically = logic.Statically(args.path)

    if args.command == "init":
        if statically.path.exists():
            print("Error: Statically instance already initialized")
            return
        statically.init()
        return

    if not statically.path.exists():
        print("Error: Please initialize a Statically instance.")
        return

    if args.command == "update":
        statically.update()
        return

def run():
    main(parse_args())
