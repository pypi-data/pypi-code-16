#!/usr/bin/env python3

from Mikado.parsers.GTF import GTF
import sys
import argparse
from collections import defaultdict


__doc__ = """"""


def main():

    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("gtf", type=GTF)
    args = parser.parse_args()

    biotypes = defaultdict(set)

    for row in args.gtf:
        biotypes[row.attributes["gene_biotype"]].add(row.source)
    args.gtf.close()

    for typ in biotypes:
        print("{0}:".format(typ))
        for name in sorted(biotypes[typ]):
            print("", "- {0}".format(name), sep="  ")

main()
