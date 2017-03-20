import h5py
import numpy as np
import argparse
import sys

def sub(parser):
    parser.add_argument('input', nargs='+', help='the samples of which to build the average of')
    parser.add_argument('output', help='to calculated average methylation values')


def run(args):
    files = [h5py.File(f, "r") for f in args.input]
    out_file = h5py.File(args.output, "w")

    chromosomes = [c for c in files[0]]

    print("building average sample", file=sys.stderr)
    for chrom in chromosomes:
        print("chromosome", chrom, file=sys.stderr)
        coverages = np.sum([np.sum(f[chrom]['methylation'][:], axis=1) > 0 for f in files], axis=0)
        coverages[coverages == 0] = 1
        sum_values = np.sum([f[chrom]['methylation'][:] for f in files], axis=0)
        mean_values = sum_values / coverages[:,None]
        grp = out_file.create_group(chrom)
        dset = grp.create_dataset("methylation", dtype='i', data=mean_values, maxshape=mean_values.shape)


#    s = np.sum([f[chrom]['methylation'] for f in files])
#    print(s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub(parser)
    args = parser.parse_args()
    mean_sample(args)
