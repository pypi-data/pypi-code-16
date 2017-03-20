import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, inspect
import matplotlib.gridspec as gridspec
import scipy.spatial.distance as distance
import scipy.cluster.hierarchy as sch
import numpy as np
import argparse

from functools import reduce
from camel.wrap.sample import Sample


def gen_data(samples, size=1000):
    sample_chromosomes = set(samples[0].chromosomes())
    chrom = [c for c in map(str, range(1,100)) if c in sample_chromosomes]

    # load coverages and methylation
    coverages = []
    M = [] 
    for s in samples:
        coverages.append(np.hstack([s.coverage(c) for c in chrom]))
        M.append(np.hstack([s.m_values(c, smooth_window=5) for c in chrom]))

    M = np.array(M).T
#    for c in coverages:
#        c[c==0] = -1

    valid = reduce(np.logical_and, [c > 10 for c in coverages])

    sd = np.std(M, axis=1) * valid
    sorted_indices = np.argsort(sd)[::-1]
    print(sorted_indices[:size])

    print(M)

    return M[sorted_indices[:size]]


# helper for cleaning up axes by removing ticks, tick labels, frame, etc.
def clean_axis(ax):
    """Remove ticks, tick labels, and frame from axis"""
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)


def plot(samples, labels=None):
    '''return fig fig of the clustering of samples'''
    # create a new figure
    fig = plt.figure(figsize=(10, 10))

    # use the top 1000 cpgs
    SIZE = 1000

    # permute test data and make dataframe
    data = gen_data(samples, SIZE)

    # reordering rows #
    pairwise_dists = distance.squareform(distance.pdist(data))

    # build the clustering
    clusters = sch.linkage(pairwise_dists,method='complete')
    dendogram = sch.dendrogram(clusters,color_threshold=np.inf,no_plot=True)

    data = data[dendogram['leaves']]

    #calculating pairwise distance matrix
    pairwise_dists = distance.squareform(distance.pdist(data.T, 'cityblock')) / SIZE
    clusters = sch.linkage(pairwise_dists,method='complete')


    #### init grid ####
    heatmap_grid = gridspec.GridSpec(2,1,wspace=0.0,hspace=0.01,height_ratios=[0.25,1])

    column_grid = gridspec.GridSpecFromSubplotSpec(2,1,subplot_spec=heatmap_grid[0,0],wspace=0.0,hspace=0.1,height_ratios=[1,0.15])


    #### dendogram ####
    sch.set_link_color_palette(['black'])
    dendogram_ax = fig.add_subplot(column_grid[0,0])
    dendogram = sch.dendrogram(clusters,color_threshold=np.inf)
    clean_axis(dendogram_ax)

    ### column colorbar ###
#    column_colorbar_ax = fig.add_subplot(column_grid[1,0])
#    column_colorbar_ax.imshow(np.array([[1] * len(samples1) + [2] * len(samples2)]),interpolation='nearest',aspect='auto',origin='lower', cmap="Set3")
#    clean_axis(column_colorbar_ax)


    #### heatmap ####
    heatmap_ax = fig.add_subplot(heatmap_grid[1,0])
    #ax = fig.add_axes([0.25, 0.25, 0.5, 0.5])
    heatmap_ax.imshow(data.T[dendogram['leaves']].T, interpolation='nearest',aspect='auto',origin='lower', cmap="RdBu_r")
    axes = heatmap_ax.get_axes()
    clean_axis(axes)


    #### col labels ####
    if not labels:
        labels = [s.basename for s in samples]

    labels = np.array(labels)
    heatmap_ax.set_xticks(np.arange(len(labels)))
    xlabelsL = heatmap_ax.set_xticklabels(labels[dendogram['leaves']])

    # rotate labels 90 degrees
    for label in xlabelsL:
        label.set_rotation(90)
    # remove the tick lines
    for l in heatmap_ax.get_xticklines() + heatmap_ax.get_yticklines(): 
        l.set_markersize(0)

    return fig


def run(args):
    samples = [Sample(s) for s in args.samples]
    fig = plot(samples, labels=args.labels)
    fig.savefig(args.output, bbox_inches='tight')


def sub(parser):
    parser.add_argument("output", help="the output file for the plot")
    parser.add_argument("--samples", nargs="+", help="methylation values in camel format")
    parser.add_argument("--labels", nargs="*", help="the labels of the samples for the clustering plot")


def main():
    parser = argparse.ArgumentParser(description='create a clustering plot')
    sub(parser)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
