import sys
from metadate import parse_date


def main():
    """ This is the function that is run from commandline with `metadate` """
    print(parse_date(" ".join(sys.argv[1:]), future=False))
