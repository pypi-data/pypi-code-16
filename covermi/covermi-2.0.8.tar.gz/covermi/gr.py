import csv, pdb
from itertools import islice
from collections import defaultdict
from operator import attrgetter
import reader
try:
    from itertools import izip as zip
except ImportError:
    pass


def bisect_right_s(a, x, lo=0, hi=None):
    """Return the index where to insert item x in list a, assuming a is sorted.
    The return value i is such that all e in a[:i] have e <= x, and all e in
    a[i:] have e > x.  So if x already appears in the list, a.insert(x) will
    insert just after the rightmost x already there.
    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        if x < a[mid].start: hi = mid
        else: lo = mid+1
    return lo


def bisect_left(a, x, lo=0, hi=None):
    """Return the index where to insert item x in list a, assuming a is sorted.
    The return value i is such that all e in a[:i] have e < x, and all e in
    a[i:] have e >= x.  So if x already appears in the list, a.insert(x) will
    insert just before the leftmost x already there.
    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        if a[mid] < x: lo = mid+1
        else: hi = mid
    return lo


class Chromosome(list):
    __slots__ = ["index"]


    def __init__(self):
        self.index = []


    def lims(self, other): # ll and ul limiting to range that could potentially overlap other
        if len(self.index) == 0:
            max_stop = 0
            for item in self:
                if item.stop > max_stop:
                    max_stop = item.stop
                self.index += [max_stop]
        if len(other.index) == 0:
            max_stop = 0
            for item in other:
                if item.stop > max_stop:
                    max_stop = item.stop
                other.index += [max_stop]
        ll = 0
        ul = len(self)
        if len(other) > 0 and len(self) > 0:
            if other[0].start > self[0].stop: # Need leftmost self that index >= other.start
                ll = bisect_left(self.index, other[0].start)
            if other.index[-1] < self[-1].start: # Need rightmost self that self.start <= other.index
                ul = bisect_right_s(self, other.index[-1]) - 1
        return (ll, ul)


    def yield_touching(self, entry):
        if len(self.index) == 0:
            max_stop = 0
            for item in self:
                if item.stop > max_stop:
                    max_stop = item.stop
                self.index += [max_stop]

        'Find leftmost item greater than or equal to pos'
        lo = 0
        hi = len(self.index)
        while lo < hi:
            mid = (lo+hi)//2
            if self.index[mid] < entry.start:
                lo = mid+1
            else: 
                hi = mid
        for index in range(lo, len(self)):
            item = self[index]
            if item.start > entry.stop:
                return
            elif item.stop >= entry.start:
                yield item



class Gr(object):

    def __repr__(self):
        return repr(self.data)


    def __init__(self, data=None):
        self.data = defaultdict(list)
        self._tuple = None
        self._hash = None
        if data is not None:
            if hasattr(data, "chrom"):
                data = (data,)
            for entry in data:
                self.add(entry)
            self.sort()


    def add(self, entry):
        self.data[entry.chrom].append(entry)
        return self


    def sort(self):
        for chrom in self.data.values():
            chrom.sort(key=attrgetter("start", "stop"))


    @property
    def sorted_by_name(self):
        for entry in sorted([entry for entry in self], key=attrgetter("name")):
            yield entry


    @property
    def all_entries(self):
        return self.__iter__()


    def __iter__(self):
        for key ,chrom in sorted(self.data.items()):
            for entry in chrom:
                yield entry


    @property
    def as_tuple(self):
        if not self._tuple: self._tuple = tuple([(key, tuple([(entry.start, entry.stop) for entry in value])) for key, value in sorted(self.data.items())])
        return self._tuple


    @property
    def as_set(self):
        return set((entry.chrom, entry.start, entry.stop) for entry in self)


    def __hash__(self):
        if not self._hash: self._hash = hash(self.as_tuple)
        return self._hash


    def __eq__(self, other):
        return self.as_tuple == other.as_tuple


    @property
    def inverted(self):
        new = type(self)()
        for key in range(0, len(reader.CHR_2_STR)):
            last_stop = 0
            if self.data[key]:
                for entry in self.data[key]:
                    if last_stop+1 < entry.start-1:
                        new.add(entry._replace(start=last_stop+1, stop=entry.start-1))
                    last_stop = entry.stop
            else:
                entry = reader.Entry(key, None, None, "", reader.PLUS)
            new.add(entry._replace(start=last_stop+1, stop=2**29-1))
        return new


    @property
    def merged(self): # The name of a range will be the name of the first sub-range that was merged into it
        new = type(self)()
        for key, chrom in self.data.items():
            nchrom = [chrom[0]]
            for entry in islice(chrom, 1, len(chrom)):
                if entry.start-1 <= nchrom[-1].stop:
                    if entry.stop > nchrom[-1].stop:
                        nchrom[-1] = nchrom[-1]._replace(stop=entry.stop)
                else:
                    nchrom.append(entry)
            new.data[key] = nchrom
        return new


    def overlapped_by(self, other):# If range other contains overlapping ranges then we may get multiple copies of the overlapping ranges
        new = type(self)()
        for key, chrom in self.data.items():
            for a in chrom:
                if key in other.data:
                    for b in other.data[key]:
                        if b.start > a.stop:
                            break
                        if (a.start <= b.start <= a.stop) or (a.start <= b.stop <= a.stop) or b.stop > a.stop:
                            new.add(a._replace(start=max(a.start, b.start), stop=min(a.stop, b.stop)))
        new.sort() # Only needed if gr contains overlapping ranges which should not happen with sane use
        return new


    def not_touched_by(self, other):
        new = type(self)()
        for key, chrom in self.data.items():
            for a in chrom:
                touching = False
                if key in other.data:
                    for b in other.data[key]:
                        if b.start > a.stop:
                            break
                        if (a.start <= b.start <= a.stop) or (a.start <= b.stop <= a.stop) or b.stop > a.stop:
                            touching = True
                            break
                if not touching:
                    new.add(a)
        return new


    def touched_by(self, other):
        new = type(self)()
        for key, chrom in self.data.items():
            for a in chrom:
                if key in other.data:
                    for b in other.data[key]:
                        if b.start > a.stop:
                            break
                        if (a.start <= b.start <= a.stop) or (a.start <= b.stop <= a.stop) or b.stop > a.stop:
                            new.add(a)
                            break
        return new


#    def touched_by(self, other):
#        new = type(self)()
#        for key, chrom in self.data.items():
#            if key in other.data:
#                otherchrom = other.data[key]
#                for entry in chrom:
#                    for otherentry in otherchrom.yield_touching(entry):
#                        new.add(entry)
#                        break
#        return new


#    def touched_by(self, other):
#        new = type(self)()
#        for key, selfchrom in self.data.items():
#            if key in other.data:
#                otherchrom = other.data[key]
#                sll, sul = selfchrom.lims(otherchrom)
#                oll, oul = otherchrom.lims(selfchrom)
#                for si in range(sll, sul):
#                    for otherentry in otherchrom.yield_touching(selfchrom[si]):
#                        new.add(selfchrom[si])
#                        break
#        return new

    
    def subranges_covered_by(self, other):
        new = type(self)()
        for key, chrom in self.data.items():
            for a in chrom:
                if key in other.data:
                    for b in other.data[key]:
                        if b.start > a.start:
                            break
                        if b.stop >= a.stop:
                            new.add(a)
                            break
        return new


    def combined_with(self, other):
        new = type(self)()
        for gr in (self, other):
            for entry in gr:
                new.add(entry)
        new.sort()
        return new


    def subset(self, names, exclude=False, genenames=False):
        if not hasattr(names, "__iter__"):
            names = (names,)
        names = set([name.split()[0] for name in names] if genenames else names)
        new = type(self)()
        for entry in self:
            if ((entry.name.split()[0] if genenames else entry.name) in names) ^ exclude:
                new.add(entry)
        return new


    @property
    def names(self):
        return sorted(set([entry.name for entry in self]))


    @property
    def number_of_components(self):
        return sum([len(chrom) for chrom in self.data.values()])


    @property
    def number_of_weighted_components(self):
        return sum([entry.weight for entry in self])


    @property
    def base_count(self):
        return sum([entry.stop - entry.start + 1 for entry in self])


    @property
    def locations_as_string(self):
        return ", ".join(["{0}:{1}-{2}".format(reader.CHR_2_STR[entry.chrom], entry.start, entry.stop) for entry in self])


    @property
    def names_as_string(self):   ###########################???
        namedict = defaultdict(list)
        for entry in self:
            try:
                namedict[entry.name].append(entry.exon)
            except AttributeError:
                pass
        namelist = []
        for name, numbers in sorted(namedict.items()):
            numbers.sort()
            exons = []
            index = 0
            while index<=len(numbers)-1:
                start = numbers[index]
                stop = start
                for index2 in xrange(index+1, len(numbers)+1):
                    if index2 == len(numbers) or numbers[index2] != stop+1:
                        break
                    stop += 1
                exons.append("e{0}{1}".format(start, "" if (start==stop) else "-{0}".format(stop)))
                index = index2
            namelist.append("{0} {1}".format(name, ",".join(exons)).strip())
        return ", ".join(namelist)


    @property
    def is_empty(self):
        return self.number_of_components == 0


    def save(self, f): #Save type(self)() object in bedfile format, START POSITION IS ZERO BASED
        try:
            writer = csv.writer(f, delimiter="\t")
        except TypeError:
            with open(f, "wb") as realfile:
                self.save(realfile)
            return
        for entry in self:
            writer.writerow((reader.CHR_2_STR[entry.chrom], entry.start-1, entry.stop, entry.name, entry.strand))
            

