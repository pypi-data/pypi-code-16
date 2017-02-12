import csv, copy, struct, pdb
from itertools import izip, izip_longest, count, ifilter, chain, repeat
from collections import defaultdict, namedtuple, Counter
from io import BufferedReader
from covermiexception import CoverMiException

try:
    import Bio.bgzf
    BGZF = True
except ImportError:
    import gzip
    BGZF = False

SPLICE_SITE_BUFFER = 5

CHR_2_STR = ["chr1",
             "chr2",
             "chr3",
             "chr4",
             "chr5",
             "chr6",
             "chr7",
             "chr8",
             "chr9",
             "chr10",
             "chr11",
             "chr12",
             "chr13",
             "chr14",
             "chr15",
             "chr16",
             "chr17",
             "chr18",
             "chr19",
             "chr20",
             "chr21",
             "chr22",
             "chrX",
             "chrY",
             "chrM",
            ]

STR_2_CHR = {"chr1": 0, "1": 0,
             "chr2": 1, "2": 1,
             "chr3": 2, "3": 2,
             "chr4": 3, "4": 3,
             "chr5": 4, "5": 4,
             "chr6": 5, "6": 5,
             "chr7": 6, "7": 6,
             "chr8": 7, "8": 7,
             "chr9": 8, "9": 8,
             "chr10": 9, "10": 9,
             "chr11": 10, "11": 10,
             "chr12": 11, "12": 11,
             "chr13": 12, "13": 12,
             "chr14": 13, "14": 13,
             "chr15": 14, "15": 14,
             "chr16": 15, "16": 15,
             "chr17": 16, "17": 16,
             "chr18": 17, "18": 17,
             "chr19": 18, "19": 18,
             "chr20": 19, "20": 19,
             "chr21": 20, "21": 20,
             "chr22": 21, "22": 21,
             "chrX": 22, "chr23": 22, "23": 22, "X": 22,
             "chrY": 23, "chr24": 23, "24": 23, "Y": 23,
             "chrM": 24, "chr25": 24, "25": 24, "M": 24,
            }

PLUS = "+"
MINUS = "-"

class FileContext(object):
    def __init__(self, fn_or_obj, mode=None):
        self.fn_or_obj = fn_or_obj
        self.mode = mode

    def __enter__(self):
        if isinstance(self.fn_or_obj, basestring):
            self.fp = open(self.fn_or_obj, self.mode)
            return self.fp
        else:
            self.fn_or_obj.seek(0)
            return self.fn_or_obj

    def __exit__(self, type_, value, traceback):
        if hasattr(self, "fp"):
            self.fp.close()


Entry = namedtuple("Entry", "chrom start stop name strand")
#VcfEntry = namedtuple("VcfEntry", "chrom start stop name strand indel quality vaf passfilter")
TranscriptEntry = namedtuple("TranscriptEntry", "chrom start stop name strand transcript")
ExonEntry = namedtuple("ExonEntry", "chrom start stop name strand exon")
VariantEntry = namedtuple("VariantEntry", "chrom start stop name strand weight")
MutationEntry = namedtuple("MutationEntry", "chrom start stop name strand weight diseases")

class VcfEntryClass(object):
    def __repr__(self):
        return "(chrom={}, start={}, stop={}, name={}, strand={}, indel={}, quality={}, vaf={}, passfilter={})".format(
                 self.chrom, self.start, self.stop, self.name, self.strand, self.indel, self.quality, self.vaf, self.passfilter)

    def __init__(self, chrom, start, stop, name, strand, indel, quality, vaf, passfilter):
        self.chrom = chrom
        self.start = start
        self.stop = stop
        self.name = name
        self.strand = strand
        self.indel = indel
        self.quality = quality
        self.vaf = vaf
        self.passfilter = passfilter

    def __eq__(self, other):
        return self.chrom == other.chrom and self.start == other.start and self.stop == other.stop and self.name == other.name

    def __hash__(self):
        return hash((self.chrom, self.start, self.stop, self.name))

CHROM = 0
POS = 1
SNPID = 2
REF = 3
ALTS = 4
QUAL = 5
FILTERS = 6
JUNK = 7
HEADINGS = 8
VALUES = 9

class Vcf(object):
    def __init__(self, path):
        self.path = path


    def __iter__(self):
        return self.read()


    def read(self):
        with FileContext(self.path, "rb") as f:
            for line in csv.reader(f, delimiter="\t"):
                if line[0].startswith("#"):
                    continue
                
                chrom = STR_2_CHR[line[CHROM]]
                quality = line[QUAL]
                quality = None if quality=="." else float(quality)
                passfilter = line[FILTERS]
                passfilter = None if passfilter == "." else all([code in ("PASS", "LowVariantFreq") for code in passfilter.split(";")])

                try:
                    ad = [float(depth) for depth in line[VALUES].split(":")[line[HEADINGS].split(":").index("AD")].split(",")]
                    dp = max(sum(ad), 1)
                except (ValueError, IndexError):
                    ad = ()
                #print line[REF], line[ALTS], "ad "+str(ad[1:])
                for start, ref, alt, depth in izip(repeat(int(line[POS])), repeat(line[REF]), line[ALTS].split(","), ad[1:]):

#                    while ref[:2] == alt[:2]:
#                        ref = ref[1:]
#                        alt = alt[1:]
#                        start += 1

#                    while ref[-1] == alt[-1] and len(ref) > 1 and len(alt) > 1:
#                        ref = ref[:-1]
#                        alt = alt[:-1]

                    length =  len(alt) - len(ref)
                    if length == 0: # snp
                        stop = start
                    elif length > 0: # insertion
                        stop = start + 1
                    else: # deletion
                        stop = start + 1 + length
                    name = "{0}:{1} {2}>{3}".format(CHR_2_STR[chrom], start, ref, alt)
#                    if length != 0:
#                        print "{} indel={} pass={}".format(name, length!=0, passfilter)

                    yield VcfEntryClass(chrom, start, stop, name, PLUS,
                                   length!=0,  quality, depth / dp if depth else None, passfilter)

    @property
    def variant_caller(self):
        with FileContext(self.path, "rb") as f:
            for line in f:
                if line.startswith("##source="):
                    return line.strip()[9:]
                if not line.startswith("#"):
                    return ""


# Bedfile format 
#    0.  Chromosome
#    1.  Start (zero based)
#    2.  End   (one based)
#    3.  Name
#    4.  Score
#    5.  Strand


CHROM = 0
START = 1
STOP = 2
NAME = 3
STRAND = 5

class Bed(object):
    def __init__(self, path):
        self.path = path


    def __iter__(self):
        return self.read()


    def read(self):
        with FileContext(self.path, "rb") as f:
            for line in csv.reader(f, delimiter="\t"):
                yield Entry(STR_2_CHR[line[CHROM]], int(line[START])+1, int(line[STOP]), line[NAME] if len(line)>NAME else ".",
                            MINUS if (len(line)>STRAND and line[STRAND]==MINUS) else PLUS)


# Ilumina Manifest file format:
#    [Header]
#
#    [Probes]
#    0.  Name-ID
#    1.  Region-ID
#    2.  Target-ID 
#    3.  Species
#    4.  Build-ID
#    5.  Chromosome
#    6.  Start position (including primer, zero based)
#    7.  End position (including primer, zero based)
#    8.  Strand
#    9.  Upstream primer sequence (len() will give primer length)
#    10  Upstream hits
#    11. Downstream  primer sequence (len() will give primer length)
#
#    [Targets]
#    0.  Target-ID
#    1.  Target-ID
#    2.  Target number (1 = on target, >1 = off target)
#    3.  Chromosome
#    4.  Start position (including primer, zero based)
#    5.  End position (including primer, zero based)
#    6.  Probe strand
#    7.  Sequence (in direction of probe strand)


HEADER = 1
PROBES = 2
TARGETS = 3

class IlluminaManifest(object):
    def __init__(self, path):
        self.path = path


    def __iter__(self):
        return self.read()


    def read(self):
        self._offtarget = []
        sections = defaultdict(int, (("Header", HEADER), ("Probes", PROBES), ("Targets", TARGETS)))
        section = HEADER
        heading_row = False
        probes = {}
        rename_offtarget = {}
        with FileContext(self.path, "rb") as f:
            for line in csv.reader(f, delimiter="\t"):

                if heading_row:
                    col = {heading: index for index, heading in enumerate(line)}
                    heading_row = False

                elif line[0].startswith("["):
                    section = sections[line[0][1:line[0].index("]")]]
                    heading_row = section!=HEADER

                elif section == PROBES:
                    probes[line[col["Target ID"]]] = (len(line[col["ULSO Sequence"]]), len(line[col["DLSO Sequence"]]))

                elif section == TARGETS:
                    chrom = STR_2_CHR[line[col["Chromosome"]]]
                    name = line[col["TargetA"]]
                    start = int(line[col["Start Position"]])
                    stop = int(line[col["End Position"]])
                    strand = line[col["Probe Strand"]]
                    target_number = line[col["Target Number"]]

                    if line[col["Target Number"]] == "1":
                        standardised_name = "{0}:{1}-{2}".format(CHR_2_STR[chrom], start, stop)
                        rename_offtarget[name] = standardised_name
                    else: # Off-target
                        standardised_name = rename_offtarget[name]

                    entry = Entry(chrom, start+probes[name][strand=="+"], stop-probes[name][strand=="-"], standardised_name, MINUS if strand=="-" else PLUS)
                    if target_number == "1": # On-target
                        yield entry
                    else:
                        self._offtarget += [entry]

    def offtarget(self):
        for entry in self._offtarget:
            yield entry


def refflatreader(f, needed, canonicaldict, doublecheck):
    for line in csv.reader(f, delimiter="\t"):
        if line[2] not in STR_2_CHR:
            continue
        if needed:
            if line[0] in needed:
                needed[line[0]] = False
            elif line[1] in needed and line[0] == doublecheck[line[1]]:
                needed[line[1]] = False
            else:
                continue
        else:
            if line[0] in canonicaldict and line[1] != canonicaldict[line[0]]:
                continue
        yield line


class RefFlat(object):
    TRANSCRIPTS = 0
    EXONS = 1

    def __init__(self, path, canonical=(), genes=(), splice_site_buffer=SPLICE_SITE_BUFFER):
        self.path = path
        canonicaldict = {} # {gene: transcript}
        for line in csv.reader(canonical, delimiter="\t"):
            canonicaldict[line[0]] = line[1].split(" ")[-1]

        needed = {} # [gene or transcript]
        doublecheck = {} # {transcript: gene}
        for line in genes:
            line = " ".join(line.split()).split() # [gene, transcript if it exists]
            if len(line):
                if len(line) == 1: # gene OR transcript only 
                    if line[0] in canonicaldict:
                        needed[canonicaldict[line[0]]] = True
                        doublecheck[canonicaldict[line[0]]] = line[0]
                    else:
                        needed[line[0]] = True
                else:
                    needed[line[1]] = True
                    doublecheck[line[1]] = line[0]
        self.canonicaldict = canonicaldict
        self.doublecheck = doublecheck
        self.needed = needed
    
        with FileContext(path, "rb") as f:
            copies = Counter()
            self.n_transcripts = Counter()
            for line in refflatreader(f, needed, self.canonicaldict, self.doublecheck):
                name = "{0} {1}".format(line[0], line[1])
                copies[name] += 1
                if copies[name] == 1:
                    self.n_transcripts[line[0]] += 1
            self.copies = {key: 1 for key, value in copies.items() if value > 1}

        missing = [key for key, value in needed.items() if value]
        if missing:
            missing = ["{0} {1}".format(doublecheck[trans], trans) if trans in doublecheck else trans for trans in missing]
            print "WARNING - {0} not found in reference file".format(", ".join(missing))        


    def read(self, what):
        copies2 = copy.copy(self.copies)
        with FileContext(self.path, "rb") as f:
            for line in refflatreader(f, self.needed, self.canonicaldict, self.doublecheck):
                transcript = "{0} {1}".format(line[0], line[1]) 
                if transcript in copies2:
                    suffix = " copy {}".format(copies2[transcript])
                    copies2[transcript] += 1
                else:
                    suffix = ""
                name = line[0] if self.n_transcripts[line[0]] == 1 else transcript
                if suffix:
                    name = "{}{}".format(name, suffix)

                chrom = STR_2_CHR[line[2]]          
                strand = MINUS if line[3]=="-" else PLUS
                if what == RefFlat.TRANSCRIPTS:
                    yield TranscriptEntry(chrom, int(line[4])+1-splice_site_buffer, int(line[5])+splice_site_buffer,  name, strand, transcript)

                elif what == RefFlat.EXONS:
                    exon_numbers = xrange(1,int(line[8])+1) if (line[3] == "+") else xrange(int(line[8]),0,-1)            
                    for start, stop, exon in izip(line[9].rstrip(",").split(","), line[10].rstrip(",").split(","), exon_numbers):
                        yield ExonEntry(chrom, int(start)+1-splice_site_buffer, int(stop)+splice_site_buffer, name, strand, exon)


class Variants(object):
    DISEASE = 0
    GENE = 1
    MUTATION = 2

    def __init__(self, path, genes=(), disease_names=()):
        self.path = path
        self.genes = set([gene.strip().split()[0] for gene in genes])
        self.disease_dict = {}
        for line in csv.reader(disease_names, delimiter="="):
            if len(line) == 2:
                self.disease_dict[line[0].strip("\" ")] = line[1].strip("\" ")


    def read(self, what):
        if what == Variants.MUTATION:
            EntryClass = MutationEntry
            mutation_disease = defaultdict(set)
        else:
            EntryClass = VariantEntry
            extra = {}
        mutations = {}
        mutation_count = Counter()
        with FileContext(self.path, "rb") as f:
            for line in csv.reader(f, delimiter="\t"):
                try:
                    chrom =STR_2_CHR[line[4]]
                except (IndexError, KeyError):
                    continue
                if self.genes and line[3] not in self.genes:
                    continue

                mutation = "{0} {1} {2}:{3}-{4}".format(line[3], line[8], CHR_2_STR[chrom], line[5], line[6])# gene mutation location
                disease = line[1].strip("\" ")
            
                try:
                    disease = self.disease_dict[disease]
                    if disease == "":
                        continue
                except KeyError:
                    pass

                if what == Variants.MUTATION:
                    name = mutation
                    mutation_disease[mutation].add(disease)
                    extra = {"diseases": disease}
                elif what == Variants.DISEASE:
                    name = disease 
                    mutation = (mutation, name)
                elif what == Variants.GENE:
                    name = line[3]

                mutations[mutation] = EntryClass(chrom, int(line[5]), int(line[6]), name, MINUS if line[7]=="-" else PLUS, 1, **extra)
                mutation_count[mutation] += 1

        for mutation, entry in mutations.items():
            if mutation_count[mutation] > 1:
                replace = {"weight": mutation_count[mutation]}
                if what == Variants.MUTATION:
                    replace["diseases"] = "; ".join(sorted(mutation_disease[mutation]))
                entry = entry._replace(**replace)
            yield(entry)


def allbins(bin, level=0, lower=0):
    higher = lower+(8**level)-1
    if bin <= higher:
        return [bin]
    bins = allbins(bin, level+1, higher+1)
    return bins + [lower + (bins[-1]-higher-1)//8]


def reg2bin(beg, end):
    beg -= 1
    end -= 1
    if ((beg>>14) == (end>>14)):
        return ((1<<15)-1)/7 + (beg>>14)
    if ((beg>>17) == (end>>17)):
        return ((1<<12)-1)/7 + (beg>>17)
    if ((beg>>20) == (end>>20)):
        return ((1<<9 )-1)/7 + (beg>>20)
    if ((beg>>23) == (end>>23)):
        return ((1<<6 )-1)/7 + (beg>>23)
    if ((beg>>26) == (end>>26)):
        return ((1<<3 )-1)/7 + (beg>>26)
    return 0


class Bai(object):

    def __init__(self, fn):
        try:
            with open(fn, "rb") as bai:
                if bai.read(4) != "BAI\1":
                    raise CoverMiException("Not a BAI file!")
                
                n_ref = struct.unpack("<i", bai.read(4))[0] # number of reference sequences
                self.bins = [defaultdict(list) for x in xrange(0, n_ref)]
                self.intervals = [() for x in xrange(0, n_ref)]
                for ref_id in xrange(0, n_ref):

                    n_bin = struct.unpack("<i", bai.read(4))[0] # number of bins for that reference sequence
                    for distinct_bin in xrange(0, n_bin):
                    
                        bin, n_chunk = struct.unpack("<Ii", bai.read(8)) # bin_number, number of chunks within that bin
                        if n_chunk:
                            if bin == 37450: # pseudo bin for unmapped reads
                                bai.read(32)
                            else:
                                chunks = [None] * n_chunk
                                for chunk in xrange(0, n_chunk):
                                    chunks[chunk] = struct.unpack("<QQ", bai.read(16))
                                self.bins[ref_id][bin] = chunks

                    n_intv = struct.unpack("<i", bai.read(4))[0] # length of linear index
                    if n_intv:
                        intervals = [None] * n_intv
                        for intv in xrange(0, n_intv):
                            intervals[intv] = struct.unpack("<Q", bai.read(8))[0]
                        self.intervals[ref_id] = intervals
        except (IOError, struct.error):
            raise CoverMiException("Truncated BAI file")
        


    def chunks(self, ref_id, start, stop):
        lower_bound = self.intervals[ref_id][(start-1)//16384]
        return sorted(itertools.ifilter(lambda x: x[1]>=lower_bound , itertools.chain([self.bins[refid][bin] for bin in allbins(reg2bin(start, stop))])))


BamStats = namedtuple("BamStats", "mapq unmapped duplicate")


class Bam(object):

    COVERAGE = 1
    STATS = 2

    Q30 = 1
    READ_LENGTH = 2

    def __init__(self, fn, index=True):
        self.bam = None
        self.bai = None
        if index and BGZF:
            try:
                self.bai = Bai(fn+".bai")
            except CoverMiException:
                pass

        try:
            self.bam = Bio.bgzf.open(fn, "rb") if BGZF else BufferedReader(gzip.open(fn, "rb"))
            if self.bam.read(4) != "BAM\1":
                self.bam.close()
                raise CoverMiException("Not a BAM file!")
            
            len_header_text = struct.unpack("<i", self.bam.read(4))[0]
            header_text = self.bam.read(len_header_text)
            num_ref_seq = struct.unpack("<i", self.bam.read(4))[0]
            self.ref_names = [None] * num_ref_seq
            for x in xrange(0, num_ref_seq):
                len_ref_name = struct.unpack("<i", self.bam.read(4))[0]
                self.ref_names[x] = self.bam.read(len_ref_name - 1)
                self.bam.read(5)
        except (IOError, struct.error):
            if self.bam: self.bam.close()
            raise CoverMiException("Truncated BAM header")
             

    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        self.bam.close()


    def coverage(self, reference=None, start=None, stop=None):
        self.unmapped = 0
        self.mapped = 0
        try:
            for vstart, vstop in self.bai.chunks(self.ref_names.index(reference), start, stop) if reference and self.bai else ((0, 0),):
                if vstart:
                    self.bam.seek(vstart)
                while True:
                    if vstop and bam.tell() > vstop:
                        break
                    read = self.bam.read(36)
                    if len(read) == 0:
                        break
                    
                    block_size, ref_id, pos, bin_mq_nl, flag_nc, len_seq, next_ref_id, next_pos, len_template = struct.unpack("<iiiIIiiii", read)
                    flag = flag_nc >> 16#// 0x10000
                    unmapped = (ref_id == -1) or (flag & 0x4)
#                    duplicate = flag & 0x400
#                    secondary = flag & 0x100
#                    supplementary = flag & 0x800

                    if unmapped: # unmapped read
                        self.bam.read(block_size-32)
                        self.unmapped += 1
                    else:

                        self.mapped += 1
                        len_read_name = bin_mq_nl & 0xFF
                        n_cigar_op = flag_nc & 0xFFFF
                        direction = MINUS if flag & 0x10 else PLUS
                        start = pos + 1

                        read_name = self.bam.read(len_read_name - 1)
                        self.bam.read(1)

                        cigar_bytes = n_cigar_op * 4
                        length = 0
                        for cigar in struct.unpack("<" + "I" * n_cigar_op, self.bam.read(cigar_bytes)):
                            cigar_op = cigar & 0xF
                            if cigar_op in (0, 2, 7, 8):
                                length += cigar // 0x10
                            elif cigar_op == 3: # skip an intron
                                if length:
                                    yield (STR_2_CHR[self.ref_names[ref_id]], start, start + length - 1, direction)
                                start += length + (cigar//0x10)
                                length = 0
                        if length:
                            yield (STR_2_CHR[self.ref_names[ref_id]], start, start + length - 1, direction)

                        self.bam.read(block_size - 32 - len_read_name - cigar_bytes)

        except (IOError, struct.error):
            self.bam.close()
            raise CoverMiException("Truncated BAM file")


    def read(self, reference=None, start=None, stop=None, what=None):
        try:
            for vstart, vstop in self.bai.chunks(self.ref_names.index(reference), start, stop) if reference and self.bai else ((0, 0),):
                if vstart:
                    self.bam.seek(vstart)
                while True:
                    if vstop and bam.tell() > vstop:
                        break
                    read = self.bam.read(36)
                    if len(read) == 0:
                        break
                    
                    block_size, ref_id, pos, bin_mq_nl, flag_nc, len_seq, next_ref_id, next_pos, len_template = struct.unpack("<iiiIIiiii", read)

                    flag = flag_nc // 0x10000
                    unmapped = (ref_id == -1) or flag & 0x10
                    duplicate = flag & 0x400
                    secondary = flag & 0x100
                    supplementary = flag & 0x800

                    len_read_name = 0
                    cigar_bytes = 0

                    if what ==  Bam.STATS:
                        mapq = (bin_mq_nl // 0x100) & 0xFF
                        yield BamStats(mapq, unmapped, duplicate)

                    elif what == Bam.COVERAGE and not (unmapped or duplicate or secondary or supplementary):
                        len_read_name = bin_mq_nl & 0xFF
                        n_cigar_op = flag_nc & 0xFFFF

                        direction = MINUS if flag & 0x10 else PLUS
                        start = pos + 1

                        read_name = self.bam.read(len_read_name - 1)
                        self.bam.read(1)

                        cigar_bytes = n_cigar_op * 4
                        length = 0
                        for cigar in struct.unpack("<" + "I" * n_cigar_op, self.bam.read(cigar_bytes)):
                            cigar_op = cigar & 0xF
                            if cigar_op in (0, 2, 7, 8):
                                length += cigar // 0x10
                            elif cigar_op == 3: # skip an intron
                                if length:
                                    yield (STR_2_CHR[self.ref_names[ref_id]], start, start + length - 1, direction)
                                start += length + (cigar//0x10)
                                length = 0
                        if length:
                            yield (STR_2_CHR[self.ref_names[ref_id]], start, start + length - 1, direction)

                    self.bam.read(block_size - 32 - len_read_name - cigar_bytes)

        except (IOError, struct.error):
            self.bam.close()
            raise CoverMiException("Truncated BAM file")


    def info(self, what, reference=None, start=None, stop=None):
        if what not in (Bam.Q30, Bam.READ_LENGTH):
            raise CoverMiException("Bam: Unknown option: {}".format(what))
        passing_q30 = 0
        total = 0
        try:
            for vstart, vstop in self.bai.chunks(self.ref_names.index(reference), start, stop) if reference and self.bai else ((0, 0),):
                if vstart:
                    self.bam.seek(vstart)
                while True:
                    if vstop and bam.tell() > vstop:
                        break
                    read = self.bam.read(36)
                    if len(read) == 0:
                        break
                    
                    block_size, ref_id, pos, bin_mq_nl, flag_nc, len_seq, next_ref_id, next_pos, len_template = struct.unpack("<iiiIIiiii", read)

                    flag = flag_nc // 0x10000
                    unmapped = (ref_id == -1) or flag & 0x10
                    duplicate = flag & 0x400
                    secondary = flag & 0x100
                    supplementary = flag & 0x800
                    n_cigar_op = flag_nc & 0xFFFF

                    if unmapped or duplicate or secondary or supplementary or n_cigar_op==0:
                        self.bam.read(block_size-32)
                        continue

                    len_read_name = bin_mq_nl & 0xFF
                    self.bam.read(len_read_name)

                    cigar_bytes = n_cigar_op * 4
                    cigar_string = [(cigar & 0xF, cigar // 0x10) for cigar in struct.unpack("<" + "I" * n_cigar_op, self.bam.read(cigar_bytes))]

                    start = 1 if cigar_string[0][0] == 5 else 0
                    if cigar_string[start][0] == 4:
                        soft_clipped = cigar_string[start][1]
                        start += 1
                    else:
                        soft_clipped = 0
                    length = sum([cigar[1] for cigar in cigar_string[start:] if cigar[0] in (0, 2, 7, 8)])
                    if what == Bam.READ_LENGTH: return length

                    self.bam.read((len_seq+1)/2)
                    quality = struct.unpack("<" + "B" * len_seq, self.bam.read(len_seq))[soft_clipped:length+soft_clipped]
                    for qual in quality:
                        if qual >= 30: passing_q30 += 1
                    total += len(quality)

                    self.bam.read(block_size - 32 - len_read_name - cigar_bytes - ((len_seq+1)/2) - len_seq)

        except (IOError, struct.error):
            self.bam.close()
            raise CoverMiException("Truncated BAM file")

        return passing_q30 * 100.0 / total if total>0 else 0
