import h5py
import numpy as np
import argparse
import sys
from camel.wrap.sample import Sample
from collections import defaultdict
from natsort import natsorted

def run(args):
    return run_direct(args.index, args.input, args.bed, args.r)


def run_direct(index_filename, input_filenames, bed_filename=None, region=None):
    samples = [Sample(filename) for filename in input_filenames]

    index = h5py.File(index_filename, "r")

    print("#chrom", "start", "stop", sep="\t", end="\t")
    print(*samples, sep="\t")

    dmrs = defaultdict(list)

    if region:
        if region.find(":") == -1:
            chrom = region
            start, stop = 0, 99999999999
        else:
            chrom, start_stop = region.split(":")
            start, stop = map(int, start_stop.split("-"))
        dmrs[chrom].append((start, stop))
    elif bed_filename:
        for line in open(bed_filename, "r"):
            line = line.strip()
            if len(line) < 2: #skip empty lines
                continue

            if line.startswith("#"): #skip comments
                continue

            split = line.split("\t")
            if len(split) < 3:
                continue

            chrom, start, stop = split[:3]
            if chrom.startswith("chr"):
                chrom = chrom[3:]
            start = int(start)
            stop = int(stop)

            dmrs[chrom].append((start, stop))
    else:
        for chrom in index:
            stop = index[chrom]["cpg_positions"][-1]
            dmrs[chrom].append((1, stop))


    for chrom in natsorted(dmrs):
        if chrom not in samples[0].chromosomes():
            print("WARNING: {chrom} not in camel file".format(chrom=chrom), file=sys.stderr)
            continue
        indices = np.searchsorted(index[chrom]["cpg_positions"][:], dmrs[chrom])
        m_values = np.array([s.m_values(chrom) for s in samples]).T

        for (start, stop), (start_index, stop_index) in zip(dmrs[chrom], indices):
            print(chrom, start, stop, sep="\t", end="\t")
            print(*(np.sum(m_values[start_index:stop_index], axis=0) / (stop_index-start_index)))
#            averages = [round(np.average(s.m_values(chrom, start_index, stop_index)),2) for s in samples]
#            print(*averages, sep="\t")


def sub(parser):
    parser.add_argument('index', help='the camel index')
    parser.add_argument('input', nargs='+', help='the samples of which to build the average of')
    parser.add_argument('--bed', help='a bed file with regions')
    parser.add_argument('--r', help='a region in the form of chr:start-stop')


def main():
    parser = argparse.ArgumentParser()
    sub(parser)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
