# -*- coding: utf-8 -*-
import logging
from operator import attrgetter
from .interval import Interval, IntervalMixin
import pysam
from .utils import fill_text, cached_property, attrdict
from builtins import zip


def parse_region(region):
    """
    Args:
        region: 1-based region
    Returns:
        (contig, start, end) 0-based coordinate
    """
    sp = region.split(':')
    contig = sp[0]
    if len(sp) == 1:
        return (contig, None, None)
    sp = sp[1].split('-')
    start = int(sp[0].replace(',', ''))
    if len(sp) == 1:
        return (contig, start - 1, None)
    return (contig, start - 1, int(sp[1].replace(',', '')))


def sam_intervals(sam, regions=None):
    """
    sam: pysam.Samfile
    """
    ref_lens = dict(zip(sam.references, sam.lengths))
    if regions is None:
        # ':' can be accidentally contained in refenrece names (e.g. HLA:HLA00001)
        for contig in sam.references:
            start = 0
            end = ref_lens[contig]
            yield Interval(contig, start, end, None)
    else:
        for r in regions:
            contig, start, end = parse_region(r)
            if start is None:
                start = 0
            if end is None:
                end = ref_lens[contig]
            yield Interval(contig, start, end, None)


import re
_blank_pat1 = re.compile('^\s+$')
def _is_blank(st):
    return bool(_blank_pat1.match(st))


# This does not work for multimapped records
class LocalInfo:
    def __init__(self, sam, iv, fasta=None, skip_flags=0x004):
        self.contig = iv.contig
        self.start = iv.start
        self.end = iv.end
        if fasta:
            fasta = pysam.Fastafile(fasta)
            ref_bases = fasta.fetch(reference=iv.contig, start=iv.start, end=iv.end).upper()
        else:
            ref_bases = '?' * (iv.end - iv.start)
        self._ref_bases = ref_bases
        self._reads = [Read(rec) for rec in sam.fetch(reference=iv.contig, start=iv.start, end=iv.end) if not rec.flag & skip_flags]

        self._bases_liss = bases_liss = []   # e.g. [['A', 'GC', '-', ...]]
        for read in self._reads:
            bases_lis = read.get_bases_list(iv.start, iv.end)
            bases_liss.append(bases_lis)

        pos_infos = []
        for bases_lis in zip(*bases_liss):
            length = max(1, max(len(b) for b in bases_lis))
            pos_infos.append({'length': length, 'bases': bases_lis})
        self._max_lens = lens = [r['length'] for r in pos_infos]
        self.align_length = sum(lens)

    def get_ref_seq(self):
        return ''.join(self._ref_bases)

    def get_ref_align(self):
        filled = [fill_text(bs, l, char='-') for l, bs in zip(self._max_lens, self._ref_bases)]   # fill missing bases
        return filled

    def iter_read_aligns(self):  # TODO sorted by position bases
        for read, bases_lis in zip(self._reads, self._bases_liss):
            filled = [fill_text(bs, l, char=(' ' if _is_blank(bs) else '-')) for l, bs in zip(self._max_lens, bases_lis)]   # fill missing bases
            yield (read, filled)

    def iter_align_pairs(self):
        """
        Yields: (Read, (aln, ref_aln))
        """
        ref_bases = self._ref_bases
        for read, bases_lis in zip(self._reads, self._bases_liss):
            b1s = []
            b2s = []
            for b1, b2 in zip(bases_lis, ref_bases):
                fill_len = max(len(b1), len(b2))
                #b1 = fill_text(b1, fill_len, char=(' ' if _is_blank(b1) else '-'))
                #b2 = fill_text(b2, fill_len, char=(' ' if _is_blank(b2) else '-'))
                b1 = fill_text(b1, fill_len, char=(' ' if _is_blank(b1) else '-'))
                b2 = fill_text(b2, fill_len, char=(' ' if _is_blank(b2) else '-'))
                b1s.append(b1)
                b2s.append(b2)
            seq1 = ''.join(b1s)
            seq2 = ''.join(b2s)
            yield read, (seq1, seq2)


def clip_seq(seq, cigar_str):
    """
    >>> clip_seq('ATCGATCG', '2M4I2M')
    'ATCGATCG'
    >>> clip_seq('ATCGATCG', '2S4I2S')
    'ATCGATCG'
    >>> clip_seq('ATCGATCG', '2H4I2H')  # only clip when hard clip
    'CGAT'
    """
    parsed = cigar_parse(cigar_str)
    if not parsed:
        return seq
    l = parsed[0][1] if parsed[0][0] == CIGAR.H else 0
    r = parsed[-1][1] if parsed[-1][0] == CIGAR.H else 0
    return seq[l:len(seq) - r]


class CIGAR:
    M = 0
    I = 1
    D = 2
    N = 3
    S = 4
    H = 5
    P = 6
    X = 7
    EQ = 8  # '='

_cigar_op_codes = dict((_op, _code) for _code, _op in enumerate('MIDNSHPX='))
_re_cigar = re.compile('(\d+)([MIDNSHPX=])')

def cigar_parse(cigar_str):
    """
    >>> cigar_parse('2I3M3D3M') == [(CIGAR.I, 2), (CIGAR.M, 3), (CIGAR.D, 3), (CIGAR.M, 3)]
    True
    >>> cigar_parse('3M2I3M2S') == [(CIGAR.M, 3), (CIGAR.I, 2), (CIGAR.M, 3), (CIGAR.S, 2)]
    True
    """
    ret = []
    for m in _re_cigar.finditer(cigar_str):
        l, op = m.groups()
        ret.append((_cigar_op_codes[op], int(l)))
    return ret


def alignment_to_cigar(aln, ref_aln):
    """
    >>> aln1 = '--------ATATGGGCCATCT'
    >>> aln2 = 'ATATATATATACGGG--ATAT'
    >>> alignment_to_cigar(aln1, aln2)
    [(2, 8), (0, 7), (1, 2), (0, 4)]
    """
    cigars = []
    op = None
    l = 0
    for a1, a2 in zip(aln, ref_aln):
        if a1 == '-':
            if op == CIGAR.D:
                l += 1
                continue
            if op is not None:
                cigars.append((op, l))
            op = CIGAR.D
            l = 1
        elif a2 == '-':
            if op == CIGAR.I:
                l += 1
                continue
            if op is not None:
                cigars.append((op, l))
            op = CIGAR.I
            l = 1
        else:
            if op == CIGAR.M:
                l += 1
                continue
            if op is not None:
                cigars.append((op, l))
            op = CIGAR.M
            l = 1
    cigars.append((op, l))
    return cigars


class Read(IntervalMixin):
    def __init__(self, rec):
        self._rec = rec
        self.name = rec.qname
        self.start = rec.pos
        self.end = rec.pos if rec.aend is None else rec.aend
        self.rec = rec   # pysam.AlignedRead
        self._seq = rec.seq
        self._bases = _get_read_bases(rec)

        self.has_lclip = (rec.qstart > 0)
        self.has_rclip = (rec.qend < rec.rlen)
        self.mapq = rec.mapq
        self.alen = 0 if self.end is None else self.end - self.start # aligned length
        self.tags = dict(rec.get_tags())
        self.edit = self.tags.get('NM', None)
        self.nins = 0
        self.ndel = 0
        for op, length in rec.cigar:
            if op == CIGAR.D:
                self.ndel += length
            elif op == CIGAR.I:
                self.nins += length

        #self.mismatches = 0
        self.qlen = rec.qlen
        self.unmapped = int(rec.is_unmapped)
        self.lclip = rec.qstart
        self.rclip = rec.rlen - rec.qend
        self.reverse = int(rec.is_reverse)
        self.suppl = int(rec.is_supplementary)
        self.read1 = int(rec.is_read1)
        self.contig = self.rname = self._rec.reference_name

        # set mate pattern
        # ---------->  ....   # right unmapped
        # ...   <----------  # left unmapped
        self.is_left = int(not rec.is_reverse)  # mate is expected to be in opposite side
        self.mate_miss = int(rec.mate_is_unmapped)
        self.mate_tid = rec.pnext
        self.tlen = tlen = rec.tlen
        # whether mate is far is determined from tlen and deviation of tlen distribution
        #self.mate_end = rec.pos + tlen if tlen > 0 else (rec.pos is rec.end is None else rec.aend) - tlen # is ok?
        self.mate_invert = 0
        self.mate_back = 0
        self.mate_jump = 0

        if self.mate_miss:
            return
        self.mate_jump = int(rec.tid != self.mate_tid)
        self.mate_invert = int(rec.mate_is_reverse == rec.is_reverse)
        if not rec.is_reverse:
            self.mate_back = int(rec.pnext < rec.pos)
        else:
            self.mate_back = int(rec.pos < rec.pnext)

    @cached_property
    def fragmented(self):
        return self.suppl or 'SA' in self.tags

    @cached_property
    def num_frags(self):
        sa = self.tags.get('SA')
        if sa is None:
            return 1
        else:
            return 1 + sa.count(';')

    @cached_property
    def edit_ratio(self):
        return 1. * self.edit / self.alen

    def get_bases_list(self, start, end):
        EMPTY = ' '
        start_offset = start - self.start
        end_offset = end - self.end
        bases = self._bases
        if start_offset > 0:
            bases = self._bases[start_offset:]
        else:
            bases = [EMPTY] * (-start_offset) + bases
        if end_offset < 0:
            bases = bases[:end_offset]
        else:
            bases = bases + [EMPTY] * end_offset
        return bases


def _get_read_bases(rec):
    '''
    Inputs:
        rec: SAM record
    Returns:
        [(A|T|C|G|-|*)+] at aligned positions

    >>> _get_read_bases(attrdict(seq='AATCAGTA', cigar=cigar_parse('2I3M3D3M')))
    ['T', 'C', 'A', '-', '-', '-', 'G', 'T', 'A']
    >>> _get_read_bases(attrdict(seq='AATCAGTACC', cigar=cigar_parse('3M2I3M2S')))
    ['A', 'A', 'TCA', 'G', 'T', 'A']
    '''
    seq = rec.seq
    # mask low qualities
    #seq = ''.join(s if q >= 10 else '.' for (s, q) in zip(seq, rec.qual))
    offset = 0
    bases = []
    for (op, length) in rec.cigar:   # TODO (show clip?)
        if op in (0, 7, 8):  # M, X, =
            bases.extend(list(seq[offset:offset + length]))
            offset += length
        elif op == 1:   # I
            if bases:   # inserted seq. at start position will be ignored
                bases[-1] += seq[offset:offset + length]  # add to prev sequence
            offset += length
        elif op == 2:   # D
            bases.extend(['-'] * length)
        elif op == 3:   # N
            bases.extend(['*'] * length)
        elif op == 4:   # S
            offset += length
        elif op == 5:   # H
            pass
        elif op == 6:   # P
            raise NotImplementedError
    return bases


class ReadCounterBase(object):
    __slots__ = ('start', 'end', 'window',)

    def __init__(self, start, window=1):
        self.start = start
        self.end = start + window

    def add(self, rec):
        """
        Add SAM Record
        """
        raise NotImplementedError


class ReadCounter(ReadCounterBase):
    def __init__(self, start, window):
        super(ReadCounter, self).__init__(start, window=window)
        self.count = 0       # qstart is contained
        self.clip = 0
        self.lclip = 0
        self.rclip = 0
        self.bclip = 0
        self.reverse = 0
        self.mapq1 = 0
        self.mate = MateInfoCounter()
        self.covlen = 0   # covered length within the bin
        self.covlen_mapq1 = 0

    def add(self, rec):
        self.count += 1
        is_lclip = (rec.qstart > 0)
        is_rclip = (rec.qend < rec.rlen)
        is_mapq1 = (rec.mapq <= 1)
        covlen = min(self.end, rec.aend) - max(self.start, rec.pos)
        self.clip += int(is_lclip or is_rclip)
        self.lclip += int(is_lclip)
        self.rclip += int(is_rclip)
        self.bclip += int(is_lclip and is_rclip)
        self.reverse += rec.is_reverse
        self.mapq1 += int(is_mapq1)
        self.mate.add(rec)
        self.covlen += covlen
        if is_mapq1:
            self.covlen_mapq1 += covlen

    def __str__(self):
        return '\t'.join((str(self.start), str(self.end), str(self.__dict__)))


class MateInfoCounter(ReadCounterBase):
    """ Count mate info
    """
    __slots__ = ('_tlen_far', 'unmapped', 'jumped', 'far', 'overlap', 'penetrate', 'rr', 'ff')
    attrs = tuple(filter(lambda x: not x.startswith('_'), __slots__))
    _getter = attrgetter(*attrs)

    def values(self):
        return self._getter(self)

    def items(self):
        return dict(zip(self.attrs, self.values()))

    def __init__(self, tlen_far=700):
        self._tlen_far = tlen_far
        self.unmapped = self.jumped = self.far = self.overlap = self.penetrate = self.rr = self.ff = 0

    def add(self, rec):
        if rec.mate_is_unmapped:
            self.unmapped += 1
            return
        if rec.rnext != rec.tid:
            self.jumped += 1
            return

        # check orientation
        if not rec.is_reverse:
            if not rec.mate_is_reverse:
                self.ff += 1
            elif rec.tlen > self._tlen_far:
                self.far += 1
            elif rec.pnext < rec.aend:
                self.overlap += 1
            elif rec.tlen < 0:
                self.penetrate += 1
        else:
            if rec.mate_is_reverse:
                self.rr += 1
            elif - rec.tlen > self._tlen_far:
                self.far += 1
            elif rec.aend - rec.pnext < - 2 * rec.tlen:  # adhoc
                self.overlap += 1
            elif rec.aend < rec.pnext:
                self.penetrate += 1

    def __str__(self):
        return str(self.items())


class BreakPointCounter(ReadCounterBase):
    def __init__(self, start, window):
        self.start = start
        self.end = start + window
        self.lclips = []

    def add(self, rec):
        self.count += 1
        is_lclip = (rec.qstart > 0)
        is_rclip = (rec.qend < rec.rlen)
        is_clip = is_lclip or is_rclip
        is_mapq1 = (rec.mapq <= 1)
        if is_lclip and self.start <= rec.pos < self.end:
            lclips.append()
        self.lclip += int(is_lclip)
        self.rclip += int(is_rclip)
        self.bclip += int(is_lclip and is_rclip)
        self.reverse += rec.is_reverse
        self.mapq1 += int(is_mapq1)
        self.mate.add(rec)
        self.covlen += covlen
        if is_mapq1:
            self.covlen_mapq1 += covlen

    def __str__(self):
        return '\t'.join((str(self.start), str(self.end), str(self.__dict__)))


class ReadCountGenerator(object):
    def __init__(self, sam, rname, start=0, end=None, window=50, mass='middle', skip_flag=0x904, counter_cls=ReadCounter):
        #self._samit = samit
        if end is None:
            rlens = dict(zip(sam.references, sam.lengths))
            end = rlens[rname]
        self._samit = sam.fetch(reference=rname, start=start, end=end)
        self.counters = []
        self.wstart = start if start % window == 0 else start // window * window # 110 -> 100, 100 -> 100, 149 -> 100  # window: 50
        self.wend = end if end % window == 0 else (end // window + 1) * window   # 110 -> 150, 100 -> 100, 149 -> 150  # window: 50
        self.cstart = self.wstart
        self.cend = self.wstart
        self.window = window
        self.skip_count = 0
        self.skip_flag = skip_flag  # unmapped, secondary or supplementary
        get_read_masses = {
            'start': lambda rec: (rec.pos,),
            'end':   lambda rec: (rec.aend - 1,),   # end position of the alignment (note that aend points one past the last aligned residue)
            'middle': lambda rec: ((rec.pos + rec.aend - 1) / 2.,),   # middle point of the alignment
            'overlap': lambda rec: range(rec.pos, rec.aend, window),   # one point per window overlaped for each alignment
        }
        self.get_read_masses = get_read_masses[mass]
        self._bulk_size = 200
        self._counter_cls = counter_cls

    def _flush(self):
        while self.counters:
            yield self._dequeue()

    def _enqueue(self):
        if self.wend is None:
            enque_size = self._bulk_size
        else:
            enque_size = min(self._bulk_size, (self.wend - self.cend) // self.window)
        self.counters.extend([self._counter_cls(self.cend + self.window * i, self.window) for i in xrange(enque_size)])
        self.cend += self.window * enque_size

    def _dequeue(self):
        self.cstart += self.window
        return self.counters.pop(0)

    def _should_skip(self, rec):
        if rec.flag & self.skip_flag:
            self.skip_count += 1
            return True

    def __iter__(self):
        try:
            while 1:
                rec = next(self._samit)
                if self._should_skip(rec):
                    continue

                start = rec.pos  # 0-based
                end = rec.aend
                while self.cend < start:
                    for counter in self._flush():
                        yield counter

                    self._enqueue()
                    #yield self._dequeue()

                while self.cend < end and self.cend < self.wend:
                    self._enqueue()

                while self.counters and self.counters[0].end < start:
                    yield self._dequeue()

                masses = self.get_read_masses(rec)
                for mass in masses:
                    rec_index = int(mass - self.cstart) // self.window
                    if 0 <= rec_index < len(self.counters):
                        self.counters[rec_index].add(rec)

        except StopIteration:
            pass
        except AssertionError as e:
            logging.error('Invalid record was found: (pos: %s, aend: %s)', rec.pos, rec.aend)
            logging.info(rec)
            raise

        for counter in self._flush():
            yield counter
