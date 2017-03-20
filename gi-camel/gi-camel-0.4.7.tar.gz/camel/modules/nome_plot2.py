import matplotlib
matplotlib.use('Agg')
import h5py
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import argparse
import os

# add parent parent path to system path
#if __name__ == "__main__":
#    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#    parentdir = os.path.dirname(os.path.dirname(currentdir))
#    os.sys.path.insert(0,parentdir)

from camel.wrap.region import Region
from camel.wrap.sample import Sample


def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    import numpy as np
    from math import factorial

    window_size = np.abs(np.int(window_size))
    order = np.abs(np.int(order))

    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')


def run(args):
    fig = plot(args.sample, args.index, args.genes, args.cgi, args.incgi, args.undirected)
    fig.savefig(args.output)


def plot(sample_filename, index_filename, genes_filename, cgi_filename, in_cpg_islands=True, undirected=False):
    fig = plt.figure(frameon=True)

    # open transcription start sites bed file:

    genes = Region(genes_filename)
    cpg_islands = Region(cgi_filename)
    sample = Sample(sample_filename)
    index = h5py.File(index_filename)

    size = 1000

    vector = np.zeros(size * 2, dtype=np.float)
    vector_cov = np.zeros(size * 2, dtype=np.float)

    for chrom in sample.chromosomes(): # for each chromosome
        if chrom not in list(map(str,range(1,23))) + ["X", "Y"]:
            continue

        if not chrom in index: # exept for these, that are not in the index
            continue

        cpg_islands_valid = cpg_islands.values["chrom"] == chrom.encode()
        cpg_islands_starts = cpg_islands.values[cpg_islands_valid]["start"]
        cpg_islands_stops = cpg_islands.values[cpg_islands_valid]["stop"]
        order = np.argsort(cpg_islands_starts)
        cpg_islands_starts = cpg_islands_starts[order]
        cpg_islands_stops  = cpg_islands_stops[order]

        value_matrix = sample.methylation(chrom, nome=True) # nome methylation values
        gpc_positions = index[chrom]["gpc_positions"][:] # get gpc positions out of the index file
        gpc_valid = index[chrom]["valid_gpc"][:]

        genes_valid = genes.values["chrom"] == chrom.encode()
        genes_values = genes.values[genes_valid]

        tss_positions = genes_values["stop"]
        directions = genes_values["direction"]
        tss_positions[directions] = genes_values["start"][directions]

        order = np.argsort(tss_positions)
        tss_positions = tss_positions[order]
        directions = directions[order]

        in_cpg_island = np.searchsorted(cpg_islands_starts,tss_positions) == np.searchsorted(cpg_islands_stops, tss_positions) + 1

        #reverse cpg valid
        if not in_cpg_islands:
            in_cpg_island = np.negative(in_cpg_island) # not in cpg_island

        tss_positions = tss_positions[in_cpg_island]
        directions = directions[in_cpg_island]

        tss_indices = np.searchsorted(gpc_positions, tss_positions)
        tss_indices_minus_1000 = np.searchsorted(gpc_positions, tss_positions - size)
        tss_indices_plus_1000 = np.searchsorted(gpc_positions, tss_positions + size)

#        print(chrom, np.sum(tss_positions), np.sum(tss_indices_minus_1000), np.sum(tss_indices_plus_1000))

        for i in range(len(tss_positions)):
            if tss_indices_minus_1000[i] == tss_indices_plus_1000[i]:
                continue

            tss_position = tss_positions[i]
            positions = gpc_positions[tss_indices_minus_1000[i]:tss_indices_plus_1000[i]]
            values = value_matrix[tss_indices_minus_1000[i]:tss_indices_plus_1000[i]]

            # correct invalid gpc
            gpc_valid_region = gpc_valid[tss_indices_minus_1000[i]:tss_indices_plus_1000[i]]

            corr_values = np.copy(values).reshape((-1,2))
            corr_values = corr_values * gpc_valid_region.reshape((-1,1))
            corr_values = corr_values.reshape((-1,4))

            meth = np.sum(corr_values[:,(0,2)], axis=1)
            cov = np.sum(corr_values, axis=1)

            cov[cov == 0] = -1
            m = meth / cov

            rel_positions = positions - tss_position + size #relative position to tss
            if not undirected:
                rel_positions *= (-1 + directions[i] * 2)

            vector[rel_positions] += m
            vector_cov[rel_positions] += (cov > 0)

    data = 1 - vector / vector_cov # building the average values


    plt.axvline(0, color='#555555')
    plt.xlabel("Distance from TSS (bp)")
    plt.ylabel("1-GpC Methylation (Nuclesome Protection)")
    plt.ylim([0.0, 1.0])
    plt.plot(np.arange(-1000,1000), data, color='#bbbbbb')
    plt.plot(np.arange(-1000,1000),savitzky_golay(data, 50, 3))
    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('index', help="The camel-index-file.")
    parser.add_argument("genes", help="List of genes in bed format.")
    parser.add_argument("cgi", help="List of cpg-islands in bed format.")
    parser.add_argument("sample", help="A sample file in camel-data format.")
    parser.add_argument("output", help="The output file. The format is chosen by the ending of this file. All matplotlib plot file formats are supported, such as pdf, svg, png or jpg.")
    parser.add_argument("-c", "--incgi", action="store_true")
    parser.add_argument("-u", "--undirected", action="store_true")

    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
