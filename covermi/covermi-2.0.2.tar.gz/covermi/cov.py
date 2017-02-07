# { chr_number : [ [start, stop, depth], [start, stop, depth] ] }

import pdb
from collections import defaultdict
from gr import Gr
import reader

PLUS = reader.PLUS
MINUS = reader.MINUS

MAX_CHR_LENGTH = 2**29 # Max length on a reference sequence in an indexed BAM + 1


def bisect_left(a, x):
    lo = 0
    hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        if a[mid][1] < x.start: lo = mid+1
        else: hi = mid
    return lo


def fake_paired_end_reads(amplicons, depth):
    for entry in amplicons.all_entries:
        third = (entry.stop - entry.start + 1) // 3
        for n in range(0, depth):
            yield (entry.chrom, entry.start, entry.stop-third, MINUS if entry.strand==MINUS else PLUS)
            yield (entry.chrom, entry.start+third, entry.stop, PLUS if entry.strand==MINUS else MINUS)


def extend(data, item):
    if len(data) and item[2] == data[-1][2]:
        data[-1][1] = item[1]
    else:
        data += [item]


def normalised(data, depth):
    newdata = defaultdict(zero_coverage)
    for key, values in data.items():
        newchrom = []
        for entry in values:
            extend(newchrom, [entry[0], entry[1], entry[2]>=depth])
        newdata[key] = newchrom
    return newdata


def combined(mydata, otherdata):
    newdata = defaultdict(zero_coverage)
    for key in set(mydata.keys()+otherdata.keys()):
         newchrom = []
         otherchrom = otherdata[key].__iter__()
         otherentry = [None, -1, None]
         for myentry in mydata[key]:
             while myentry[0] > otherentry[1]:
                 otherentry = otherchrom.next()
             while otherentry[1] < myentry[1]:
                 extend(newchrom, [max(myentry[0], otherentry[0]), otherentry[1], myentry[2]+otherentry[2]])
                 otherentry = otherchrom.next()
             extend(newchrom,[max(myentry[0], otherentry[0]), myentry[1], myentry[2]+otherentry[2]])
         newdata[key] = newchrom
    return newdata


class CumCov(object):

    def __init__(self):
        self._data = defaultdict(zero_coverage)
        self.number = 0


    def add(self, other, depth):
        self.number += 1
        self._data = combined(self._data, normalised(other.data, depth))
        return self


    @property
    def data(self):
        newdata = defaultdict(zero_coverage)
        for key, chrom in self._data.items():
            newchrom = []
            for entry in chrom:
                newchrom += [[entry[0], entry[1], entry[2]*100/self.number]]
            newdata[key] = newchrom
        return newdata


def zero_coverage(): return [[0, MAX_CHR_LENGTH, 0]]


class Cov(object):

    def __init__(self, data, amplicons=()):
        self.data = defaultdict(zero_coverage)

        if isinstance(data, basestring):
            bam = reader.Bam(data)
            data = bam.coverage()
        else:
            bam = None

        fr_depth = {}
        self.amplicon_info = []
        self.ontarget = 0
        self.offtarget = 0
        for amplicon in amplicons:
            amplicon_info = AmpliconInfo(amplicon)
            self.amplicon_info += [amplicon_info]
            fr_depth[(amplicon.start, PLUS)] = amplicon_info
            fr_depth[(amplicon.stop, MINUS)] = amplicon_info

        for chrom, start, stop, strand in data:
            depth = 1
            cov = self.data[chrom]
            upperx = -1
            lowerx = -1
            for x in xrange(len(cov) - 1, -1, -1):
                if stop < cov[x][0]:
                    continue
                if stop >= cov[x][1] and start <= cov[x][0]:
                    cov[x][2] += depth
                    if start == cov[x][0]:
                        break
                else:
                    if stop < cov[x][1]:
                        upperx = x
                    if start > cov[x][0]:
                        lowerx = x
                        break
            if upperx != -1:
                cov.insert(upperx, [cov[upperx][0], stop, cov[upperx][2] + depth])
                cov[upperx+1][0] = stop + 1
            if lowerx != -1:
                cov.insert(lowerx+1, [start, cov[lowerx][1], cov[lowerx][2] + depth * (upperx!=lowerx)])
                cov[lowerx][1] = start - 1
                if upperx == lowerx:
                    cov[lowerx][2] -= depth

            if amplicons:
                try:
                    fr_depth[(start, PLUS)].f_depth += 1
                    self.ontarget += 1
                except KeyError:
                    try:
                        fr_depth[(stop, MINUS)].r_depth += 1
                        self.ontarget += 1
                    except KeyError:
                        self.offtarget += 1                        

        self.amplicon_info.sort()
        if bam:
            self.unmapped = bam.unmapped
            self.mapped = bam.mapped


    def load(self, path):
        self.__init__()
        with open(path, "rb") as f:
            for line in csv.reader(f, delimiter="\t"):
                self.data[line[0]].append([int(value) for value in line[1:4]])


    def save(self, path):
        with open(path, "wb") as f:
            writer = csv.writer(f, delimiter="\t")
            for chrom in self:
                for entry in self[chrom]:
                    writer.writerow([chrom]+entry)


    def calculate(self, gr1, min_depth, exons=False, total=False):
        results = defaultdict(CoverageInfo)
        for entry in gr1.all_entries:
            name = entry.name if (not total) else ""
            name = name if (not exons) else "{0} e{1}".format(name, entry.exon)
            info = results[name]
            info.name = name
            info.diseases = getattr(entry, "diseases", "")

            allcovered = True
            cchrom = self.data[entry.chrom]
            bisect = bisect_left(cchrom, entry) # leftmost coverage.stop >= entry.start
            for cstart, cstop, cdepth in cchrom[bisect:]:
                if cstart > entry.stop:
                    break
                elif cstop >= entry.start:
                    bases = min(entry.stop, cstop) - max(entry.start, cstart) + 1
                    if cdepth>=min_depth:
                        info.bases_covered += bases
                        info.depth_covered += bases * cdepth
                        info.range_covered.add(entry._replace(start=max(entry.start, cstart), stop=min(entry.stop, cstop)))
                    else:
                        info.bases_uncovered += bases
                        info.depth_uncovered += bases * cdepth
                        info.range_uncovered.add(entry._replace(start=max(entry.start, cstart), stop=min(entry.stop, cstop)))
                        allcovered = False
            if allcovered:
                info.components_covered += 1
                info.weighted_components_covered += getattr(entry, "weight", 0)
            else:
                info.components_uncovered += 1
                info.weighted_components_uncovered += getattr(entry, "weight", 0)

        results = sorted(results.values())
        for info in results:
            info.depth_covered /= max(info.bases_covered, 1)
            info.depth_uncovered /= max(info.bases_uncovered, 1)
            info.range_covered = info.range_covered.merged
            info.range_uncovered = info.range_uncovered.merged
        return results if (not total) else results[0]


class AmpliconInfo(object):

    def __repr__(self):
        return "{} forward={} reverse={}".format(self.entry, self.f_depth, self.r_depth)

    def __init__(self, entry):
        self.entry = entry
        self.f_depth = 0
        self.r_depth = 0

    def __lt__(self, other):
        return self.entry < other.entry

    @property
    def name(self):
        return self.entry.name

    @property
    def chrom(self):
        return reader.CHR_2_STR[self.entry.chrom]

    @property
    def minimum_depth(self):
        return min(self.f_depth, self.r_depth)

    @property
    def maximum_depth(self):
        return max(self.f_depth, self.r_depth)

    @property
    def mean_depth(self):
        return (self.f_depth + self.r_depth)/2

    @property
    def ratio(self):
        return float(self.minimum_depth)/max(self.maximum_depth, 1)

    @property
    def gr(self):
        return Gr().add(self.entry)


class CoverageInfo(object):

    def __repr__(self):
        return "{} {}%".format(self.name, self.percent_covered)

    def __init__(self):
        self.name = ""
        self.diseases = ""
        self.depth_covered = 0
        self.depth_uncovered = 0
        self.bases_covered = 0
        self.bases_uncovered = 0
        self.range_covered = Gr()
        self.range_uncovered = Gr()
        self.components_covered = 0
        self.components_uncovered = 0
        self.weighted_components_covered = 0
        self.weighted_components_uncovered = 0

    def __lt__(self, other):
        return self.name < other.name
    
    @property
    def depth(self):
        return ((self.depth_covered * self.bases_covered) + (self.depth_uncovered + self.bases_uncovered)) / self.bases

    @property
    def percent_covered(self):
        return float(self.bases_covered*100) / self.bases

    @property
    def percent_uncovered(self):
        return 100 - self.percent_covered

    @property
    def range_combined(self):
        return self.range_covered.combined_with(self.range_uncovered).merged

    @property
    def bases(self):
        return self.bases_covered + self.bases_uncovered

    @property
    def components(self):
        return self.components_covered + self.components_uncovered

    @property
    def percent_components_covered(self):
        return float(self.components_covered*100) / self.components

    @property
    def percent_components_uncovered(self):
        return 100 - self.percent_components_covered

    @property
    def weighted_components(self):
        return self.weighted_components_covered + self.weighted_components_uncovered

    @property
    def percent_weighted_components_covered(self):
        return float(self.weighted_components_covered*100) / self.weighted_components

    @property
    def percent_weighted_components_uncovered(self):
        return 100 - self.percent_weighted_components_covered

    @property
    def completely_covered(self):
        return not(self.incompletely_covered)

    @property
    def incompletely_covered(self):
        return bool(self.bases_uncovered)
