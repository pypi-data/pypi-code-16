import argparse
import os
from .gen import CodeWordGenerator


def parse_args():
    """Parse command line arguments."""
    CW_ADJECTIVES = os.getenv("CW_ADJECTIVES", None)
    CW_NOUNS = os.getenv("CW_NOUNS", None)
    CW_DELIMITERS = os.getenv("CW_DELIMITERS", None)
    parser = argparse.ArgumentParser()
    parser.add_argument("--adjectives", default=CW_ADJECTIVES)
    parser.add_argument("--nouns", default=CW_NOUNS)
    parser.add_argument("--delimiters", default=CW_DELIMITERS)
    parser.add_argument("--pattern", default=None)
    return parser.parse_args()


def main():
    args = parse_args()

    g = CodeWordGenerator(adjfilename=args.adjectives, nounfilename=args.nouns,
                          delimiterfilename=args.delimiters)
    print(g.generate(args.pattern))


if __name__ == '__main__':
    main()
