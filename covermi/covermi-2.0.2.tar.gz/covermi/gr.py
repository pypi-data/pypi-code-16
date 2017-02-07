import csv, pdb
from itertools import islice
from collections import defaultdict
from operator import attrgetter
import reader
try:
    from itertools import izip as zip
except ImportError:
    pass


class Gr(object):

    def __repr__(self):
        return repr(self.data)


    def __init__(self, data=None):
        self.data = defaultdict(list)
        self._tuple = None
        self._hash = None
        if data is not None:
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


    def __hash__(self):
        if not self._hash: self._hash = hash(self.as_tuple)
        return self._hash


    def __eq__(self, other):
        return self.as_tuple == other.as_tuple


    @property
    def inverted(self):
        new = type(self)()
        for key, chrom in self.data.items():
            last_stop = 0
            for entry in chrom:
                if last_stop+1 < entry.start-1:
                    new.add(entry._replace(start=last_stop+1, stop=entry.start-1))
                last_stop = entry.stop
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
            

