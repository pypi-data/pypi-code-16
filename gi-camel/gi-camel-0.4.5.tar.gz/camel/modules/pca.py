import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os, inspect
import matplotlib.gridspec as gridspec
import scipy.spatial.distance as distance
import scipy.cluster.hierarchy as sch
import numpy as np
import h5py
import argparse
from matplotlib.font_manager import FontProperties

from functools import reduce

from camel.wrap.sample import Sample
from camel.helper.common import savitzky_golay

from sklearn.decomposition import PCA

sns.set_style("whitegrid")

def gen_data(samples):
    sample_chromosomes = set(samples[0].chromosomes())
    chromosomes = [c for c in map(str, range(1,100)) if c in sample_chromosomes]

    M = []

    for chrom in chromosomes:
        print("loading chromosome {}".format(chrom))
        coverages = [s.coverage(chrom) for s in samples]

        for c in coverages:
            c[c==0] = -1

        val = reduce(np.logical_and, [c > 10 for c in coverages])

        M.append(np.array([s.m_values(chrom, smooth_window=10) for s in samples]))

    return np.hstack(M)

#    sd = np.std(M, axis=0) * val
#    sorted_indices = np.argsort(sd)[::-1]
#    return M.T[sorted_indices[:size]]


def plot(samples, labels=[], colors=[], markers=[]):
    '''return pca plot figure for samples'''
    # create a new figure
    fig = plt.figure(figsize=(10, 10))

    # permute test data and make dataframe
    data = gen_data(samples)

    print("received data, calculating plot")

    pca = PCA(n_components=2)
    proj = pca.fit_transform(data)
    #PCA(copy=True, n_components=2, whiten=False)
#    print("explained_variance_ratio_", pca.explained_variance_ratio_)

    if not colors:
        colors = ['black'] * len(samples)

    if not markers:
        markers = ['o'] * len(samples)


    if not labels:
        labels = samples

    fig = plt.figure()


    g = sns.pointplot(proj[:,0], proj[:,1], color="#336699", marker='o', join=False, dodge=False)
    g.cla()

    #g.plot(0, 0, color="red", marker="o", ms=0, label="test")

    for x, y, c, m, l in zip(proj[:,0], proj[:,1], colors, markers, labels):
        g.plot(x, y, color=c, alpha=0.6, marker=m, ms=13, label=l, linestyle="")

    explained_variance_ratio = pca.explained_variance_ratio_

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlabel("PC1 ({0:.2f} explained variance)".format(explained_variance_ratio[0]))
    plt.ylabel("PC2 ({0:.2f} explained variance)".format(explained_variance_ratio[1]))

    return fig


def run(args):
    samples = [Sample(s) for s in args.samples]
    fig = plot(samples, labels=args.labels, colors=args.colors, markers=args.markers)
    fig.savefig(args.output, bbox_inches='tight')


def sub(parser):
    parser.add_argument("output", help="the output file for the plot")
    parser.add_argument("--samples", nargs="+", help="methylation values in camel format")
    parser.add_argument("--labels", nargs="*", help="the labels of the samples for the clustering plot")
    parser.add_argument("--colors", nargs="*", help="the colors of the markers")
    parser.add_argument("--markers", nargs="*", help="the style of the markers, use matplotlib maker symbols")


def main():
    parser = argparse.ArgumentParser(description='create a clustering plot')
    sub(parser)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
