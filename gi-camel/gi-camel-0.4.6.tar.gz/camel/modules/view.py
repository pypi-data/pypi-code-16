import argparse
import h5py
import numpy as np
import sys
from collections import namedtuple

Location = namedtuple("Location", "chrom, start, stop")

def parse_region(region):
    split = region.split(':')
    if len(split) == 1:
        chrom, = split
        return Location(chrom, -1, -1)
    chrom, positions = split
    split = positions.split('-')

    if len(split) == 1:
        start, = split
        return Location(chrom, int(start), -1)

    start, stop = split
    return Location(chrom, int(start), int(stop))

def out_native(chrom, methylation, positions):
    meth = methylation[:]
    stack = np.hstack((positions, meth))
    fmt = "{chrom}\t%i\t%i\t%i\t%i\t%i".format(chrom=chrom)
    return (stack, fmt)


def out_merged(chrom, methylation, positions):
    meth = methylation[:]
    cov = np.sum(meth, axis=1).reshape(-1,1)

    m = np.sum(meth[:,(0,2)], axis=1).reshape(-1,1)

    stack = np.hstack((positions, m, cov))


    fmt = "{chrom}\t%i\t%i\t%i".format(chrom=chrom)
    return (stack, fmt)


def out_simple(chrom, methylation, positions):
    meth = methylation[:]
    cov = np.sum(meth, axis=1)
    cov_plus = np.copy(cov)
    cov_plus[cov_plus==0] = 1

    m = np.sum(meth[:,(0,2)], axis=1)
    rel = np.round((m*100 / cov_plus)).astype(np.int32).reshape((-1,1))
    stack = np.hstack((positions, rel))
    fmt = "{chrom}\t%i\t%i".format(chrom=chrom)
    return (stack, fmt)


def out_epp(chrom, methylation, positions):
    plus_minus = np.empty(shape=(len(methylation[:]) * 2), dtype=np.int32)
    plus_minus[::2] = ord("+")
    plus_minus[1::2] = ord("-")

    positions_doubled = np.hstack((positions - 1, positions - 1)).flatten()

    cov = np.sum(methylation[:].reshape((-1,2)), axis=1)
    cov_plus = np.copy(cov)
    cov_plus[cov_plus==0] = 1

    meth = methylation[:].reshape((-1,2))[:,0]

    rel = (meth*1000 / cov_plus).astype(np.int32)
    stack = np.vstack((positions_doubled, positions_doubled + 2, meth, cov, rel, plus_minus)).T
    fmt = "chr{chrom}\t%i\t%i\t'%i/%i'\t%i\t%c".format(chrom=chrom)

    return (stack, fmt)


def out_bismark_cov(chrom, methylation, positions):
    positions_doubled = np.hstack((positions, positions+1)).flatten()

    cov = np.sum(methylation[:].reshape((-1,2)), axis=1)
    cov_plus = np.copy(cov)
    cov_plus[cov_plus==0] = 1

    meth = methylation[:].reshape((-1,2))[:,0]
    umeth = methylation[:].reshape((-1,2))[:,1]

    rel = np.round((meth*100 / cov_plus)).astype(np.int32)
    stack = np.vstack((positions_doubled, positions_doubled, rel, meth, umeth)).T
    fmt = "chr{chrom}\t%i\t%i\t%i\t%i\t%i".format(chrom=chrom)
    return (stack, fmt)


def out_bed(chrom, methylation, positions):
    meth = methylation[:]
    cov = np.sum(meth, axis=1)
    cov_plus = np.copy(cov)
    cov_plus[cov_plus==0] = 1

    m = np.sum(meth[:,(0,2)], axis=1)
    rel = np.round((m*100 / cov_plus)).astype(np.int32).reshape((-1,1))
    stack = np.hstack((positions, positions+1, rel))
    fmt = "{chrom}\t%i\t%i\t%i".format(chrom=chrom)
    return (stack, fmt)


def out_granges(chrom, methylation, positions):
    meth = methylation[:]
    cov = np.sum(meth, axis=1).reshape((-1,1))
    m = np.sum(meth[:,(0,2)], axis=1).reshape((-1,1))

    stack = np.hstack((positions, positions, cov, m))

    sys.stdout.buffer.write(b"\t".join([b"seqnames", b"start", b"end", b"width", b"strand", b"T", b"M"])) #header
    sys.stdout.buffer.write(b"\n") #header
    fmt = "chr{chrom}\t%i\t%i\t1\t*\t%i\t%i".format(chrom=chrom)
    return (stack, fmt)


def __data__(samples, index, region=None, style="native"):
    samples = h5py.File(samples, 'r')
    index = h5py.File(index, 'r')

    coverage = False

    if region:
        region = parse_region(args.region)
        chromosomes = [region.chrom]
    else:
        chromosomes = [i for i in samples if not i == "meta"] # TODO change structure


    for chrom in chromosomes:
#        coverages = np.sum(samples[chrom]['methylation'][:], axis=1)
#        fix_coverages = coverages[:]
#        fix_coverages[coverages == 0] = 1 # fix coverage = 0
#        meth = np.sum(samples[chrom]['methylation'][:,(0,2)], axis=1)
#        ratio = meth * 100 / fix_coverages

        cpgs = index[chrom]["cpg_positions"]

        if region: 
            start_index = np.searchsorted(cpgs, region.start) if region.start > -1 else 0
            stop_index = np.searchsorted(cpgs, region.stop) + 1 if region.stop > -1 else -1 # TODO: +1 includes the last position if it equals a cpg position

            positions = cpgs[start_index:stop_index].reshape((-1,1))
            methylation = samples[chrom]["methylation"][start_index:stop_index]
        else:
            positions = cpgs[:].reshape((-1,1))
            methylation = samples[chrom]["methylation"]

        # choose output style
        if style == "native":
            out_func = out_native
        if style == "merged":
            out_func = out_merged
        elif style == "simple":
            out_func = out_simple
        elif style == "epp":
            out_func = out_epp
        elif style == "bismarkCov":
            out_func = out_bismark_cov
        elif style == "granges":
            out_func = out_granges
        elif style == "bed":
            out_func = out_bed

        stack, fmt = out_func(chrom, methylation, positions)
        yield chrom, stack, fmt


def data_dict(samples, index, region=None):
    for chrom, stack, fmt in __data__(samples, index, region, "merged"):
        for x in stack:
            yield {
                "chrom": chrom,
                "pos": x[0],
                "methylation": x[1],
                "coverage": x[2],
            }


def run(args):
    for chrom, stack, fmt in __data__(args.input, args.index, args.region, args.style):
        try:
            np.savetxt(sys.stdout.buffer, stack, fmt=fmt)
        except IOError:
            break


def sub(p):
    p.add_argument('input', help='the hdf5 file')
    p.add_argument('index',help='the index file')
    p.add_argument('region', nargs='?', help='a region to output', default=None)
#    p.add_argument('--epp', action='store_true', default=False)

    p.add_argument('--style', '-s', choices=["native", "merged", "simple", "epp", "bismarkCov", "granges", "bed"], default="native")
    p.add_argument('-c', action='store_true', default=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub(parser)
    args = parser.parse_args()
    run(args)
