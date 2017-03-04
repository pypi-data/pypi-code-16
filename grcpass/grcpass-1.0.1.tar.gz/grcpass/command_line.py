#!/usr/bin/env python

import argparse
import grcpass

def main():
    parser = argparse.ArgumentParser(description='Simple password fetcher - https://github.com/arturtamborski/grcpass')
    parser.add_argument('--hex',   action='store_true', dest='hex',   help='64 random hexadecimal characters')
    parser.add_argument('--ascii', action='store_true', dest='ascii', help='63 random printable ASCII characters')
    parser.add_argument('--alpha', action='store_true', dest='alpha', help='63 random alpha-numeric characters [a-zA-Z0-9]')
    args = parser.parse_args()

    if not args.hex and not args.ascii and not args.alpha:
        parser.print_help()
        return -1

    passwords = grcpass.generate()

    if args.hex:
        print(passwords.hex)

    if args.ascii:
        print(passwords.ascii)

    if args.alpha:
        print(passwords.alpha)

if __name__ == '__main__':
    main()
