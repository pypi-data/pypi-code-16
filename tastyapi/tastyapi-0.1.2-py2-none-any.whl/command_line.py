import tastyapi
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('get_user', help='Query information on a specific user', type=str)
    parser.add_argument('-j','--json', help='Return unformatted JSON', action='store_true')
    args = parser.parse_args()
    if args.get_user:
        if args.json:
            return tastyapi.get_user(args.get_user)
        return tastyapi.get_user(args.get_user)
