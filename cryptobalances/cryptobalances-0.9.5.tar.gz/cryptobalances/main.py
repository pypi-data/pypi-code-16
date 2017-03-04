# -*- coding: utf-8 -*-
import argparse
from cryptobalances.checker import get_request


def main():
    parser = argparse.ArgumentParser(description='Getting balance of wallet of your crypto currency')
    parser.add_argument('currency', nargs='?', type=str, help='Type of currency')
    parser.add_argument('wallet', nargs='?', type=str, help='Identifier of wallet')
    args = parser.parse_args()
    if (args.currency and args.wallet) is not None:
        print(get_request(args.currency)(args.currency, args.wallet))


if __name__ == "__main__":
    main()
