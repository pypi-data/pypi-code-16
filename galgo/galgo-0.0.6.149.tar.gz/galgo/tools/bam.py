from __future__ import print_function
from argtools import command, argument
import pysam
from pysam import Samfile
import re
import logging
from builtins import filter, zip
from ..utils import fill_text
from ..bioseq import color_term_dna, get_aln_pos_text, dna_revcomp
from ..samutil import LocalInfo, sam_intervals, Read, clip_seq
from operator import attrgetter


@command.add_sub
@argument('bamfile')
@argument('bamout')
@argument('-u', '--unpaired')
@argument('-f', '--uncount-flag', type=lambda x: int(x, 16), default=0x900, help='uncount-flag for existing reads; default is secondary or supplementary reads')
def bam_discard_unpaired(args):
    sam = pysam.Samfile(args.bamfile)
    read1s = set()
    read2s = set()
    uncount_flag = args.uncount_flag
    for rec in sam:
        if rec.flag & uncount_flag:
            continue
        if rec.is_read1:
            read1s.add(rec.qname)
        else:
            read2s.add(rec.qname)

    paired = read1s & read2s
    unpaired = (read1s - paired) | (read2s - paired)
    logging.info('Paired reads: %s', len(paired))
    logging.info('Unpaired reads: %s', len(unpaired))

    sam.reset()
    out = pysam.Samfile(args.bamout, mode='wb', template=sam)
    out2 = pysam.Samfile(args.unpaired, mode='wb', template=sam) if args.unpaired else None
    for rec in sam:
        if rec.qname in paired:
            # workaround for avoiding duplicated emission of the same record
            if rec.is_read1:
                if rec.qname in read1s:
                    out.write(rec)
                    read1s.remove(rec.qname)
            else:
                if rec.qname in read2s:
                    out.write(rec)
                    read2s.remove(rec.qname)
        elif out2:
            out2.write(rec)


@command.add_sub
@argument('bamfile')
@argument('-l', '--list')
@argument('--max-edit', type=int, help='use NM tag')
@argument('-o', '--output', default='/dev/stdout')
def bam_filter(args):
    sam = pysam.Samfile(args.bamfile)
    if args.output.endswith('.bam'):
        mode = 'wb'
    else:
        mode = 'wh'
    out = pysam.Samfile(args.output, mode=mode, template=sam)

    if args.list:
        white_list = set([name.rstrip() for name in open(args.list)])
        def list_filter(sam):
            for rec in sam:
                if rec.qname in white_list:
                    yield rec

        sam = list_filter(sam)

    if args.max_edit is not None:
        max_edit = args.max_edit
        def is_ok(rec):
            tag = dict(rec.get_tags())
            edit = tag.get('NM', 0)
            return edit <= max_edit
        sam = filter(is_ok, sam)

    for rec in sam:  # fetch only primary and non-supplementary reads
        out.write(rec)


@command.add_sub
@argument('bamfile')
@argument('-r', '--region')
def bam_profile(args):
    """
    """
    sam = pysam.Samfile(args.bamfile)
    attrs = ['name', 'read1', 'unmapped', 'suppl', 'num_frags', 'qlen', 'rname', 'start', 'end', 'alen', 'mapq', 'reverse', 'lclip', 'rclip', 'edit', 'nins', 'ndel']
    getter = attrgetter(*attrs)
    with sam:
        print (*(attrs + ['tags_md']), sep='\t')
        for rec in sam.fetch(args.region):
            r = Read(rec)
            print (*(getter(r) + (dict((k, v) for k, v in rec.tags if k != 'MD'),)), sep='\t')


# TODO sort by read_name, read_length, ref_identity, ref_diversity <= weighted identity (using base probability as weight is ok)
# show read properties (mismatch on reads
@command.add_sub
@argument('bam')
@argument('region', nargs='+')  # TODO currently, need this option
@argument('-r', '--reference')
@argument('-c', '--color-base', action='store_true')
@argument('-m', '--mask-ref-base', action='store_true')
@argument('--order', help='sort orders: select from qname, edit, nins, ndel, alen, <ref_pos>'.format())
@argument('-R', '--reverse', action='store_true')
def bam_aln_view(args):
    """
    """
    sam = Samfile(args.bam)
    skip_flags = 0x004
    sep = ' ' * 10
    sep = '\t'
    def decorate(aln, ref_aln=None, indicator=None):
        if ref_aln and args.mask_ref_base:
            #aln = ''.join(('.' if a == r and a != ('-' or ' ') else a) for a, r in zip(aln, ref_aln))
            aln = ''.join(('.' if a == r else a) for a, r in zip(aln, ref_aln))  # '-' is also shown as '.'
        if indicator:
            # if aln is blank, fill with indicator instead
            aln = ''.join(i if a == ' ' else a for a, i in zip(aln, indicator))
        if args.color_base:
            aln = color_term_dna(aln)
        return aln

    def get_sorted(read_alns):
        if args.order is None:
            return read_alns
        # if args.order.isdigit():  # TODO getting corresponding reference position is required
        #     pos = int(args.order)
        #     read_alns = sorted(read_alns, key=lambda x: x[1], reversed=args.reverse)
        order = args.order
        assert order in 'qname edit edit_ratio nins ndel alen'.split(' ')
        return sorted(read_alns, key=lambda x: getattr(x[0], order), reverse=args.reverse)

    logging.info('Target region: %s', args.region)
    with sam:
        for iv in sam_intervals(sam, regions=(args.region or None)):
            loc = LocalInfo(sam, iv, fasta=args.reference, skip_flags=skip_flags)
            print ('start', loc.start)
            print ('end', loc.end)
            print ('align length', loc.align_length)
            ref_aln = ''.join(loc.get_ref_align())
            ref_dec = decorate(ref_aln)
            pos_txt = get_aln_pos_text(ref_aln, offset=loc.start)
            indicator = pos_txt['indicator']
            print (pos_txt['number'])
            print (indicator)
            print (ref_dec, iv.contig, 'mapq', 'clip', 'edit', 'nins', 'ndel', 'alen', 'edit_ratio', sep=sep)
            indicator = indicator.replace('|', ':')  # for visibility
            print (indicator)
            it = loc.iter_read_aligns()
            it = get_sorted(it)
            for read, aln in it:
                read_aln = decorate(''.join(aln), ref_aln, indicator=indicator)
                clip_status = ('1' if read.has_lclip else '0') + ('1' if read.has_rclip else '0')
                print (read_aln, read.rec.qname, read.mapq, clip_status, read.edit, read.nins, read.ndel, read.alen,
                        '{0:.2f}'.format(read.edit_ratio), sep=sep)


@command.add_sub
@argument('bam')
@argument('-r', '--region', help='region of target bam file')
@argument('-s', '--source-bam')  # TODO pair of fastq
@argument('-o', '--output', default='/dev/stdout')
def bam_fill_seq(args):
    """ Fill empty sequence with known seqs
    """
    if not args.source_bam:
        source_bam = args.bam
    else:
        source_bam = args.source_bam
    logging.info('Loading samfile: %s', source_bam)
    src_seqs = {1: {}, 2: {}}

    src = pysam.Samfile(source_bam)
    with src:
        for rec in src:
            if rec.is_supplementary:  # skip supplementary alignment
                continue
            if rec.is_secondary:  # skip supplementary alignment
                continue
            if rec.seq is None:  # empty
                continue
            if rec.is_read1:
                src_seqs[1][rec.qname] = (rec.seq, rec.is_reverse)
            else:
                src_seqs[2][rec.qname] = (rec.seq, rec.is_reverse)

    logging.info('Loaded read1 : %s', len(src_seqs[1]))
    logging.info('Loaded read2 : %s', len(src_seqs[2]))

    sam = Samfile(args.bam)
    if args.output.endswith('.bam'):
        mode = 'wb'
    else:
        mode = 'wh'
    out = pysam.Samfile(args.output, mode=mode, template=sam)

    if args.region:
        it = sam.fetch(region=args.region)
    else:
        it = sam

    for rec in it:
        qname = rec.qname
        if rec.seq is None:  # only fill when empty
            ret = src_seqs[1 if rec.is_read1 else 2].get(rec.qname)
            if ret is not None:
                seq, is_rev = ret
                if is_rev != rec.is_reverse:
                    seq = dna_revcomp(seq)
                seq = clip_seq(seq, rec.cigarstring)
                rec.seq = seq  # refill

        out.write(rec)
