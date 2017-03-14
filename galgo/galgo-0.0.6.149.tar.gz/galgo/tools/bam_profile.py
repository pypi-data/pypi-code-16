from __future__ import print_function
from argtools import command, argument
import logging
import os
import tempfile
import pysam
import numpy as np
import pandas as pd
from .. import plot
from .. import sh


class SamMethods(object):
    def __init__(self, sam):
        self._sam = sam
        self.filename = sam.filename
        index1 = '{0}.bai'.format(sam.filename)
        index2 = '{0}.bai'.format(sam.filename.rsplit('.', 2)[0])
        #if os.path.exists(index1):  # no use
        #    self.indexpath = index1
        #elif os.path.exists(index2):
        #    self.indexpath = index2
        #else:
        #    self.indexpath = None

    def _gen_it(self, chroms=None):
        if chroms is None:
            for rec in self._sam:
                yield rec
        else:
            for chrom in chroms:
                sam_it = self._sam.fetch(reference=chrom)
                for rec in sam_it:
                    yield rec

    def estimate_mean_rlen(self, chroms=None, rsample=1000, use_alen=False, skip_flag=0x900):
        """ rough estimattion
        """
        lens = []
        if use_alen:
            get_length = lambda rec: rec.alen
        else:
            get_length = lambda rec: len(rec.seq)

        sam_it = self._gen_it(chroms=chroms)
        try:
            i = rsample
            while i:
                rec = next(sam_it)
                if not (rec.flag & skip_flag):
                    lens.append(get_length(rec))
                    i -= 1

        except StopIteration:
            pass
        self._sam.reset()
        return np.mean(lens)

    def get_reference_length(self, chroms=None):
        if chroms is None:
            return sum(self._sam.lengths) - nlen
        chrom_set = set(chroms)
        tlen = sum(length for ref, length in zip(self._sam.references, self._sam.lengths) if ref in chrom_set)
        return tlen

    def _get_index_stats(self):
        with tempfile.NamedTemporaryFile() as fp:
            logging.info('Emit index_stats to %s', fp.name)
            sh.call(['samtools', 'idxstats', self.filename], stdout=fp.name)
            tab = pd.read_table(fp, header=None, names=['reference', 'length', 'mapped', 'unmapped'])
        return tab

    def get_mapped(self, chroms=None):
        if chroms is None:
            return self._sam.mapped
        stats = self._get_index_stats()
        chrom_set = set(chroms)
        maps = [mapped for chrom, mapped in zip(stats.reference, stats.mapped) if chrom in chrom_set]
        return sum(maps)


class Nbed(object):
    def __init__(self, nbed):
        self._tab = pd.read_table(nbed, header=None, names=['contig', 'start', 'end'])

    def get_length(self, contig):
        return (self._tab.end - self._tab.start)[self._tab.contig == contig].sum()


@command.add_sub
@argument('bamfile')
@argument('-r', '--rsample', type=int, default=1000)
def bam_mean_rlen(args):
    sam = pysam.Samfile(args.bamfile, 'rb')
    samm = SamMethods(sam)
    rlen = samm.estimate_mean_rlen(rsample=args.rsample)
    print (rlen)


@command.add_sub
@argument('bamfile')
def bam_mean_cov(args):
    """ Emit mean coverage (#reads) per base
    """
    sam = pysam.Samfile(args.bamfile, 'rb')
    totlen = sum(sam.lengths)    # reference length (contains N)
    cov = 1. * sam.mapped / totlen # (mapped may contains secondary or supplementary alignments)
    print (cov)


@command.add_sub
@argument('bamfile')
@argument('-r', '--rsample', type=int, default=1000)
@argument('--pacbio', action='store_true', help='use suplementary alignemnt, use only aligned length')
@argument('--nbed', help='N bed regions')
@argument.exclusive(
    argument('--chroms', nargs='+'),
    argument('--autosomal', action='store_true'),
)
def bam_mean_depth(args):
    """ Roughly estimate bam depth

    - estimate mean read length by scanning top {rsample} reads
    - divide the total length by total reference lengths

    # TODO autosomal option
    """
    sam = pysam.Samfile(args.bamfile, 'rb')
    samm = SamMethods(sam)
    if args.autosomal:
        if 'chr1' in sam.references:
            chroms = ['chr' + str(i + 1) for i in range(22)]
        else:
            chroms = [str(i + 1) for i in range(22)]
    else:
        chroms = args.chroms

    if args.pacbio:
        logging.info('PacBio mode')
        rlen = samm.estimate_mean_rlen(rsample=args.rsample, chroms=chroms, use_alen=True, skip_flag=0x104)
    else:
        rlen = samm.estimate_mean_rlen(rsample=args.rsample, chroms=chroms)
    totlen = samm.get_reference_length(chroms=chroms)

    # negating N bases if available
    nlen = 0
    if args.nbed:
        nbed = Nbed(args.nbed)
        if chroms is None:
            nlen = sum(nbed.get_length(ref) for ref in sam.references)
        else:
            chrom_set = set(chroms)
            nlen = sum(nbed.get_length(ref) for ref in sam.references if ref in chrom_set)

    logging.info('Negating N region from total length: %s', nlen)
    mapped = samm.get_mapped(chroms=chroms)
    d = 1. * mapped * rlen / (totlen - nlen) # (mapped may contains secondary or supplementary alignments)
    logging.info('chroms: %s', chroms)
    logging.info('Sampled reads: %s', args.rsample)
    logging.info('Estimated mean read length: %s', rlen)
    logging.info('Total mapped fragments: %s', mapped)
    logging.info('Total refenrece length: %s', totlen)
    print (d)


@command.add_sub
@argument('bamfile')
@argument('-r', '--region')
@argument('-p', '--plot')
def bam_stats_len(args):
    """ Default is length show distribution
    """
    skip_flags = 0x800 | 0x100  # ignore secondary or suppl. alignment
    sam = pysam.Samfile(args.bamfile, mode='rb', check_sq=False)  # check_sq=False is required for PacBio bam
    if args.region:
        samit = sam.fetch(region=args.region)
    else:
        samit = sam

    lengths = []
    for rec in samit:
        logging.debug(rec)
        if rec.flag & skip_flags:
            continue
        length = rec.infer_query_length(always=False)
        if length is None:
            length = rec.query_length
        lengths.append(length)

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    lens = pd.Series(lengths)
    print (lens.describe())
    if args.plot:
        logging.info('Plot to %s', args.plot)
        plot.init()
        lens.hist(bins=100)
        plt.savefig(args.plot)
