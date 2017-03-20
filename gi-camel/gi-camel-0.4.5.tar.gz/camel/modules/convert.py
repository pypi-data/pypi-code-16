'''converts a textfile to a camel-data-file'''

import h5py
import numpy as np
import argparse
import sys
import gzip

from camel.wrap.sample import Sample

def run(args):
    return run_direct(args.index, args.input, args.output, args.seperator, args.skiplines)


def write(index, chrom, positions, ms, covs, outfile):

    chrom_positions = index[chrom.decode()]["cpg_positions"][:]
    indices = np.searchsorted(chrom_positions, positions)
    chrom_pos_verify_values = chrom_positions[indices]
    valid = positions == chrom_pos_verify_values

    indices = indices[valid]
    positions = np.array(positions)[valid]
    ms = np.array(ms)[valid]
    covs = np.array(covs)[valid]

    final = np.zeros((len(chrom_positions), 4))
    final[:,0][indices] = ms
    final[:,1][indices] = covs - ms

    grp = outfile.create_group(chrom)
    dset = grp.create_dataset("methylation", dtype='i', data=final, maxshape=final.shape)


def run_direct(index_filename, input_filename, output_filenames, seperator="\t", skiplines=0):
    index = h5py.File(index_filename, "r")
    outfile = h5py.File(output_filenames, "w")

    curr_chrom = ""

    for i,line in enumerate(gzip.open(input_filename, "r")):
        if i < skiplines:
            continue

        split = line.strip().split(seperator.encode())
        chrom = split[0]

        if chrom.startswith(b"chr"):
            chrom = chrom[3:]

        if curr_chrom != chrom:
            if len(curr_chrom):
                write(index, curr_chrom, positions, ms, covs, outfile)
            positions = []
            ms = []
            covs = []
            curr_chrom = chrom
            print(curr_chrom.decode(), file=sys.stderr)

        positions.append(int(split[1])) #positions
        ms.append(int(split[2])) #m_values
        covs.append(int(split[3])) #coverages

    write(index, curr_chrom, positions, ms, covs, outfile)

    outfile.close()



def sub(parser):
    parser.add_argument('index', help='the camel index')
    parser.add_argument('input', help='the sample in text format')
    parser.add_argument('output', help='the filename of the resulting camel-data-file (.h5)')
    parser.add_argument('-s', "--seperator", default="\t", help='the seperator, that seperates the values')
    parser.add_argument('-l', "--skiplines", default=0, type=int, help="skip the first x lines")


def main():
    parser = argparse.ArgumentParser()
    sub(parser)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
