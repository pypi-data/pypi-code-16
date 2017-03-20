import numpy as np
import math
import h5py
import os
import sys
import operator
from functools import reduce
import argparse

from numpy.lib.recfunctions import merge_arrays

def load(filename, chrom, min_cov=10):
    f = h5py.File(filename, "r")
    values = f[chrom]["methylation"][:]
    m = np.sum(values[:,(0,2)], axis=1)
    cov = np.sum(values, axis=1)

    cov[cov == 0] = 1
    m_values = m / cov

    return m_values, cov < min_cov


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
    return run_direct(args.index, args.case, args.control, args.min_cpg, args.min_diff, args.min_cov, args.smooth)


def run_direct(index_filename, case, control, min_cpg=1, min_diff=0, min_cov=10, smooth=False):
    index = h5py.File(index_filename, "r")

    for chrom in map(str, range(1,23)): #range(1,23)
        values_case, invalid_case = zip(*[load(s, chrom, min_cov) for s in case])
        values_control, invalid_control = zip(*[load(s, chrom, min_cov) for s in control])

        #smooth values
#        values_case = list(map(lambda x: savitzky_golay(x, 3, 3), values_case))
#        values_control = list(map(lambda x: savitzky_golay(x, 3, 3), values_control))

        #invalid stored a vector for each position, where at least one coverage is to low
        invalid = reduce(operator.or_, invalid_case + invalid_control)

        #"filter" low coverage
        for value in values_case + values_control:
            value[invalid] = 0

        n_case = len(values_case)
        n_control = len(values_control)

        # calculate means
        mean_case = np.mean(values_case, axis=0)
        mean_control = np.mean(values_control, axis=0)

        # calculate differences and standard deviation
        betas = mean_control - mean_case
        omega = (np.std(values_case + values_control, axis=0) + np.std(values_control, axis=0)) / 2

        #calculate the omega 75th percentile
        omega_perc = np.percentile(omega, 75)

        #cap the omega values to the percentile
        omega[omega >  omega_perc] = omega_perc

        #TODO: smooth the omegas with running mean 101 window

        #form t statistic
        t = np.divide(betas, omega * math.sqrt(1/n_case + 1/n_control))

#        print(t[1873967-4:1873997+10])

#        exit()

        if True:
            t = savitzky_golay(t, 10, 3)

#        print(t[1873967-4:1873997+10])

        t_extend = np.concatenate(([0], t, [0])) # to make sure every dmr has a start and an end


        #TODO: do not delete for further analysis
        #for v, b in zip(*np.histogram(t, range=(-10, 10), bins=100)):
        #    print(b, v, sep="\t")


        over = np.zeros(len(t_extend))
        over[(t_extend > 6) | (t_extend < -6)] = 1
        over_diff = np.diff(over)

        starts = np.where(over_diff==1)[0]
        ends   = np.where(over_diff==-1)[0]

        # the numbers of cpg per dmr
        cpg_count = ends - starts

        # determine the beta value between the dmrs
        cumsum = np.cumsum(betas)


        dmr_betas = np.divide(cumsum[ends - 1] - cumsum[starts - 1], cpg_count) #TODO wahrscheinlich +- 1 auf die indices

        # correct first DMR beta value if the first t-value is significant and the "start" -1 therefore adresses -1, which means the last index
        if starts[0] == 0:
            dmr_betas[0] = cumsum[ends[0] - 1] / cpg_count[0]


        # only dmrs with beta > 0.4 and more than 8 cpg
        selection = (np.abs(dmr_betas) >= min_diff) & (cpg_count >= min_cpg)

        starts_filtered = starts[selection]
        ends_filtered = ends[selection]
        cpg_count = cpg_count[selection]
        dmr_betas = dmr_betas[selection]

        cpg_pos = index[chrom]["cpg_positions"][:]


        m = merge_arrays((np.repeat(chrom, len(starts_filtered)), cpg_pos[starts_filtered], cpg_pos[ends_filtered], cpg_count, dmr_betas), asrecarray=True)
        m.dtype.names = ("chrom", "start", "stop", "n", "diff")

        yield m


def out(x):
    for i in x:
        for a in i:
            print(*a, sep="\t")


def sub(parser):
    # add items to a parser or subparser
    parser.add_argument('index', help='the camel index file')
    parser.add_argument("--case", nargs="+", help="the case samples in camel format")
    parser.add_argument("--control", nargs="+", help="the control samples in camel format")
    parser.add_argument("--min_cpg", default=1, type=int, help="the minimum number of CpGs to call a region")
    parser.add_argument("--min_diff", default=0.0, type=float, help="the minimum mean difference to call a region")
    parser.add_argument("--min_cov", default=10, type=int, help="the minimum coverage for each cpg")
    parser.add_argument("--smooth", action="store_true", help="the methylation varlues get smoothed")



def main():
    parser = argparse.ArgumentParser(description='Calculate methylation level for each CpG.')
    sub(parser)
    args = parser.parse_args()
    out(run(args))


if __name__ == '__main__':
    main()
