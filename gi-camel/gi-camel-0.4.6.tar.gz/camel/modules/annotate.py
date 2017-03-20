import argparse
import numpy as np
from camel.wrap.region import Region


def run(args):
    out(args)


def run_direct(dmrs_filename, track_filename, name="ann", type="overlap", n=1):
    region = Region(track_filename)

    for line in open(dmrs_filename):
        line = line.strip()

        if line.startswith('#'):
            print(line.strip(), name + ".count", sep='\t')
            continue

        if not line:
            continue

        split = line.split('\t')
        chrom, start, stop = split[:3]

        if type=="overlap":
            annotation_values, typs, dists = region.overlap(chrom.encode(), start, stop)
            yield (line, annotation_values, typs, dists)
        elif type=="nearest":
            annotation_values, typs, dists = region.nearest(chrom.encode(), start, stop, n)
            yield (line, annotation_values, typs, dists)
        elif type=="neighbours":
            annotation_values, typs, dists = region.neighbours(chrom.encode(), start, stop)
            yield (line, annotation_values, typs, dists)



def out(args):
    if args.type == "overlap":
        ana_type="overlap"
    elif args.type == "overlap-count":
        ana_type="overlap"
    elif args.type == "nearest":
        ana_type="nearest"
    elif args.type == "neighbours":
        ana_type="neighbours"

    data = run_direct(args.dmrs, args.track, args.name, ana_type, args.number)

    for dmr, annotation, typ, dist in data:
        print(dmr, end="\t")
        if args.type == "overlap":
            names = [a["name"].decode() for a in annotation]
            print(*names, sep=",")
        elif args.type == "overlap-count":
            print(len(annotation))
        elif args.type == "nearest":
            names = [a["name"].decode() for a in annotation]
            distances = [dists for a in annotation]
            print(*names, sep=",", end="\t")
            print(*distances, sep=",")
        elif args.type == "neighbours":
            names = [a["name"].decode() for a in annotation]
            distances = [dists for a in annotation]
            print(*names, sep=",", end="\t")
            print(*distances, sep=",")

#        elif len(annotation) == 0:
#            print("\t")
#        else:
#            print(*[a["name"].decode() for a in annotation], sep=",")


def sub(parser):
    parser.add_argument('dmrs', help="the track with the DMRs")
    parser.add_argument('track', help="the track with the annotation data")
    parser.add_argument('name', help="the prefix-name of the new annotation column")
    parser.add_argument('--type', '-t', choices=["overlap", "overlap-count", "nearest", "neighbours"], default="overlap")
    parser.add_argument('--number', '-n', default=1, type=int)


def main():
    parser = argparse.ArgumentParser(description='Annotate DMRs by track')
    sub(parser)
    args = parser.parse_args()
    out(args)


if __name__ == '__main__':
    main()
