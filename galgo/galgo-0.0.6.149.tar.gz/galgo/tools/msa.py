from __future__ import print_function
from ..utils import Counter, cached_property
from .fasta import iter_contigs, Contig   # TODO deprecated
from ..bioseq import color_term_dna, mask_same_bases, Fasta, get_aln_pos_text, mask_unknown_seq, SeqLocator, contig2chain, AlignmentAnalyzer
from builtins import zip
from argtools import command, argument
import itertools
import logging
import pandas as pd


@command.add_sub
@argument('fasta', help='all contigs should be the same lengths')
@argument('-n', '--name', default='new_contig', help='name of new contig')
def msa_consensus(args):
    """ Make a consensus sequence from multiple aligned contigs
    """
    contigs = list(iter_contigs(args.fasta))
    seqs = list(contig.seq for contig in contigs)

    def iter_consensus():
        for bases in zip(*seqs):
            counts = Counter(filter(lambda x: x !='-', bases))
            if not counts:  # no bases other than padding '-'
                yield ''
            else:
                cons_base = counts.most_common(1)[0][0]
                yield cons_base

    new_seq = ''.join((base for base in iter_consensus()))

    print ('>' + args.name)
    print (new_seq)


@command.add_sub
@argument('fasta', help='all contigs should be the same lengths')
@argument('-f', '--from-name', default='1', help='name of new contig')
@argument('-t', '--to-name', default='2', help='name of new contig')
def msa2chain(args):
    """ Make chain file from a pair of aligned contigs (default pair is 1st and 2nd)
    """
    with open(args.fasta) as fp:
        fasta = Fasta(fp)
        if args.from_name.isdigit():
            from_contig = fasta.contigs[int(args.from_name) - 1]
        else:
            from_contig = fasta.get(args.from_name)
        if args.to_name.isdigit():
            to_contig = fasta.contigs[int(args.to_name) - 1]
        else:
            to_contig = fasta.get(args.to_name)

        chain = contig2chain(from_contig, to_contig)
        print ('chain', *chain['header'], sep=' ')
        for row in chain['data']:
            print (*row, sep='\t')


# TODO realign option
@command.add_sub
@argument('fasta', help='all contigs should be the same lengths')
@argument('-n', '--names', help='comma separated list of names to calculate')
@argument('-r', '--redundant', action='store_true', help='calculate for all the combinations')
@argument('--ctx-size', type=int, default=3, help='when set this, emit CTX base context sequences for edits')
def msa2edit(args):
    """ Calculate pairwise edit distance from multiple aligned contigs

    Emission records:
        name1 :
        name2 :
        pos  : 123  # pos in alignment
        pos1 : 121  # last end in contig 1 (last pos if seq is deletion)
        pos2 : 122  # last end in contig 2 (last pos if seq is deletion)
        seq1 : A
        seq2 : -
        ctx_size : 3
        ctx1 : AAAAAAA
        ctx2 : AAA-AAA

    # TODO collapsing neighbor variants
    """
    assert args.ctx_size > 0
    with open(args.fasta) as fp:
        fasta = Fasta(fp)
        if args.names:
            names = args.names.split(',')
        else:
            names = fasta.names

        if args.redundant:
            pairs = itertools.product(names, names)
        else:
            pairs = itertools.combinations(names, 2)
        ctx_size = args.ctx_size

        print ('name1', 'name2', 'msa_pos', 'pos1', 'pos2', 'base1', 'base2', 'ctx_size', 'ctx1', 'ctx2', sep='\t')
        for n1, n2 in pairs:
            c1 = fasta.get(n1)
            aln1 = c1.seq.upper()
            c2 = fasta.get(n2)
            aln2 = c2.seq.upper()
            aa = AlignmentAnalyzer(aln1, aln2)
            for pos, b1, b2 in aa.iter_edits():
                ctx = aa.get_context(pos, left=args.ctx_size, right=args.ctx_size+1)
                pos1 = ctx['last_end1']
                pos2 = ctx['last_end2']
                ctx1 = ctx['ctx1']
                ctx2 = ctx['ctx2']
                print (n1, n2, pos, pos1, pos2, b1, b2, ctx_size, ctx1, ctx2, sep='\t')


# TODO realign option
@command.add_sub
@argument('fasta', help='all contigs should be the same lengths')
@argument('-n', '--names', help='comma separated list of names to calculate')
@argument('-r', '--redundant', action='store_true', help='calculate for all the combinations')
def msa2dist(args):
    """ Calculate pairwise edit distance from multiple aligned contigs

        name1 :
        name2 :
        distance : distance
        ins : ins from name1 to name2
        del : del from name1 to name2
        mut : mutation
    """
    with open(args.fasta) as fp:
        fasta = Fasta(fp)
        if args.names:
            names = args.names.split(',')
        else:
            names = fasta.names

        if args.redundant:
            pairs = itertools.product(names, names)
        else:
            pairs = itertools.combinations(names, 2)

        print ('name1', 'name2', 'alen', 'len1', 'len2', 'distance', 'ins', 'del', 'mut', sep='\t')
        for n1, n2 in pairs:
            c1 = fasta.get(n1)
            aln1 = c1.seq.upper()
            c2 = fasta.get(n2)
            aln2 = c2.seq.upper()
            aa = AlignmentAnalyzer(aln1, aln2)

            ins = del_ = mut = 0
            for pos, b1, b2 in aa.iter_edits():
                if b1 == b2:
                    logging.warning('not an edit: (%s, %s, %s)', pos, b1, b2)
                elif b1 == '-':
                    ins += 1
                elif b2 == '-':
                    del_ += 1
                elif b1 != b2:
                    mut += 1
            dist = ins + del_ + mut
            alen = len(aln1)
            len1 = len(aln1.replace('-', ''))
            len2 = len(aln2.replace('-', ''))
            print (n1, n2, alen, len1, len2, dist, ins, del_, mut, sep='\t')


class MSAPileup:
    """
    >>> p1 = MSAPileup(['A', 'A', '*'])
    >>> p1.width, p1.is_variant
    (1, False)
    >>> p1.masks
    (False, False, True)

    >>> p2 = MSAPileup(['A', 'T', '*'])
    >>> p2.width, p2.is_variant
    (1, True)
    >>> p2.masks
    (False, False, True)

    >>> MSAPileup.merge(p1, p2).masks
    (False, False, True)

    >>> p3 = MSAPileup(['*', 'T', 'G'])
    >>> p3.width, p3.is_variant
    (1, True)
    >>> p3.masks
    (True, False, False)

    >>> p4 = MSAPileup.merge(p1, p2, p3)
    >>> p4.width
    3
    >>> p4.bases
    ['AA*', 'ATT', '**G']
    >>> p4.masks
    (False, False, False)
    """

    def __init__(self, bases, pos=None, names=None, mask_char='*'):
        self.bases = bases
        self.width = len(bases[0])
        self.base_counts = Counter(self.bases)
        self.mask_char = mask_char
        self.pos = pos
        self.names = names

    @cached_property
    def masks(self):
        mask_base = self.mask_char * self.width
        return tuple(b == mask_base for b in self.bases)

    @cached_property
    def is_variant(self):
        if self.width > 1:
            warnings.warn('Variant determination for pileup with width > 1 may be inaccurate')
        if self.mask_char * self.width in self.base_counts:
            return len(self.base_counts) > 2
        else:
            return len(self.base_counts) > 1

    @staticmethod
    def merge(*pileups):
        head = pileups[0]
        bases = [''.join(bs) for bs in zip(*(p.bases for p in pileups))]
        return MSAPileup(bases, pos=head.pos, names=head.names, mask_char=head.mask_char)


def iter_msa_pileup(fasta, names=None, variant_only=False, merge_variant=False):
    contigs = fasta.contigs
    if names:
        contig_map = dict((c.name, c) for c in contigs)
        contigs = [contig_map[name] for name in names]
    else:
        names = fasta.names

    mask_char = '*'
    #seq_iters = [iter(c.get_clip_mask_seq(mask_char=mask_char), None) for c in contigs]
    seq_iters = [iter(mask_unknown_seq(c.seq.upper, mask_char=mask_char), None) for c in contigs]
    pos = 0  # 0 start
    buffer = []

    while 1:
        bases = map(next, seq_iters)
        if bases[0] is None:
            break

        pileup = MSAPileup(bases, pos, names, mask_char=mask_char)
        if (pileup.is_variant and merge_variant
            and (not buffer or buffer[0].masks == pileup.masks)):  # mask positions are the same
            buffer.append(pileup)
        else:
            if buffer:
                p = MSAColumn.merge(*buffer)
                yield p
                buffer = []
            if not variant_only:
                yield pileup
        pos += 1
    if buffer:
        p = MSAPileup.merge(*buffer)
        yield p


def msa2df(fasta):
    tab = pd.DataFrame()
    for contig in fasta.contigs:
        contig.name
        seq = contig.get_clip_mask_seq()
        tab[contig.name] = pd.Series(list(seq))
    return tab


@command.add_sub
@argument('fasta', help='all contigs should be the same lengths')
@argument('-p', '--show-position', action='store_true')
@argument('-c', '--color', action='store_true')
@argument('-m', '--mask', action='store_true')
@argument('-u', '--mask-unknown-bases', action='store_true')
#@argument('-d', '--diff', action='store_true', help='only show positions with difference')
#@argument('-r', '--range', action='store_true', help='only show positions with difference')
#@argument('-n', '--ref-name', help='default is consensus')
#@argument('-i', '--ref-index', type=int, help='if specified, ref_name is ignored')   # consensus
def msa_view(args):
    """ Make a consensus sequence from multiple aligned contigs
    """
    def decorate(seq, ref=None):
        if args.mask_unknown_bases:
            seq = mask_unknown_seq(seq, mask_char='_')
        if args.mask and ref is not None:
            seq = mask_same_bases(seq, ref)
        if args.color:
            seq = color_term_dna(seq)
        return seq

    with open(args.fasta) as fp:
        fasta = Fasta(fp)

        it = iter(fasta)
        #it = iter_contigs(fp)
        contig = next(it)
        ref = contig.seq.upper()
        pos_text = get_aln_pos_text(ref, count_del=True)
        print (pos_text['number'], sep='\t')
        print (pos_text['indicator'], sep='\t')
        pos_text = get_aln_pos_text(ref, count_del=False)
        print (pos_text['number'], sep='\t')
        print (pos_text['indicator'], sep='\t')
        print (decorate(ref), 0, contig.name_line, sep='\t')
        for idx, contig in enumerate(it, 1):
            seq = contig.seq.upper()
            #pos_text = get_aln_pos_text(seq)
            #print (pos_text['number'], sep='\t')
            #print (pos_text['indicator'], sep='\t')
            #seq = ' ' * contig.lclip + seq[contig.lclip : len(seq) - contig.rclip] + ' ' * contig.rclip
            print (decorate(seq, ref=ref), idx, contig.name_line.replace('\t', ' '), sep='\t')


@command.add_sub
@argument('fasta', help='all contigs should be the same lengths')
@argument('--layout', help='layout file')
@argument('--fig-x', type=float, default=8.3)
@argument('--fig-y', type=float, default=10.7)
@argument('--title', default='MSA layout plot')
@argument('--adjust-right', type=float, default=.8)
def msa_layout_plot(args):
    """
    layout is tsv file
        name:
        show_name:
        type: [gene,exon]
        parent: name
        show_offset:
        show_diff: [01]   # annotate difference
        # show_variant: [01]
        color: e.g. 'red'
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    matplotlib.rcParams['figure.figsize'] = (args.fig_x, args.fig_y)  # A4
    matplotlib.rcParams['font.size'] = 10.
    matplotlib.rcParams['axes.titlesize'] = 'medium'
    matplotlib.rcParams['axes.labelsize'] = 'medium'
    matplotlib.rcParams['axes.labelpad'] = 8.
    matplotlib.rcParams['xtick.labelsize'] = 'small'
    matplotlib.rcParams['ytick.labelsize'] = 'small'
    matplotlib.rcParams['legend.fontsize'] = 'small'
    tab = pd.read_table(args.layout)
    out = '{0}.pdf'.format(args.layout)
    logging.info('Create %s', out)

    with open(args.fasta) as fp:
        fasta = Fasta(fp)
        name_contigs = dict(zip(fasta.names, fasta.contigs))
        fig = plt.figure()
        #ax = fig.add_subplot(111, aspect='equal')
        ax = plt.gca()
        y_margin = 100
        offset = 100
        height = 50
        y_ids = []
        id_names = {}

        for row in tab.itertuples():
            print (row)
            name = row.name
            if name not in name_contigs:
                logging.warning('%s is not included in MSA', name)
                continue
            parent = row.parent if isinstance(row.parent, int) else 0
            if parent and (parent not in id_names or id_names[parent] not in name_contigs):
                logging.warning('%s is not included in MSA', name)
                continue
            if not parent:
                y_index = len(y_ids)
                id_names[row.id] = name
                y_ids.append(row.id)
            else:
                y_index = y_ids.index(parent)

            color = row.color
            seq = mask_unknown_seq(name_contigs[name].seq)
            loc = SeqLocator(seq)
            end = len(seq)
            y = y_index * y_margin
            for s, e, t in loc.blocks:
                x = s
                width = e - s
                print (x, y, width, height)
                ax.add_patch(patches.Rectangle((x, y), width, height, facecolor=color))
            if not parent:
                ax.text(end + offset, y + y_margin*.5, row.show_name)
        ax.set_aspect('equal')
        ax.set_xlim(0, end + offset)
        ax.set_ylim(y + y_margin , - y_margin)
        ax.get_yaxis().set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.xaxis.set_ticks_position('bottom')
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        #ax.set_frame_on(False)
        ax.set_title(args.title)
        plt.subplots_adjust(left=.05, right=args.adjust_right)
        plt.savefig(out)
