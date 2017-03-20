import sys
import numpy as np
import h5py
from collections import defaultdict, namedtuple
from functools import lru_cache
from numpy.lib.recfunctions import append_fields, rec_append_fields

class Region:
    Reg = namedtuple("Reg", "start stop direction value")


    def __init__(self, filename):
        self.open_txt(filename)


    def clear_chrom(self, chrom):
        if chrom.startswith(b"chr"):
            chrom = chrom[3:]
        return chrom


    def open_txt(self, filename):
        '''open the bed file'''
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith("#"): continue
                break

        column_count = len(line.split("\t"))

        if column_count == 3:
            dtype = [('chrom','a25'),('start','i8'),('stop','a25')]
            converters = {0: lambda x: self.clear_chrom(x)} #TODO: keep that? maybe optional
            values = np.genfromtxt(filename, dtype=dtype, converters=converters)
            names = np.repeat("", len(values))
            directions = np.repeat(True, len(values))
            self.values = append_fields(values, ("name", "direction"), (names, directions))
        elif column_count == 4:
            dtype = [('chrom','a25'),('start','i8'),('stop','i8'),('name','a25')]
            converters = {0: lambda x: self.clear_chrom(x)}
            values = np.genfromtxt(filename, dtype=dtype, converters=converters)
            directions = np.repeat(True, len(values))
            self.values = append_fields(values, ("direction"), (directions))
        elif column_count == 5:
            dtype = [('chrom','a25'),('start','i8'),('stop','i8'),('name','a25'),('score','i8')]
            converters = {0: lambda x: self.clear_chrom(x)}
            values = np.genfromtxt(filename, dtype=dtype, converters=converters)
            directions = np.repeat(True, len(values))
            self.values = append_fields(values, ("direction"), (directions))
        elif column_count == 6:
            dtype = [('chrom','a25'),('start','i8'),('stop','i8'),('name','a25'),('score','i8'),('direction', 'bool')]
            converters = {0: lambda x: self.clear_chrom(x), 5: lambda x: x == b"+"}
            values = np.genfromtxt(filename, dtype=dtype, converters=converters)
            self.values = values
        else:
            sys.exit("invalid number of columns in track")



    def overlap(self, chrom, start, stop):
        '''return list of items that overlap with a given region'''

        chrom = self.clear_chrom(chrom)
        start = int(start)
        stop = int(stop)
        mid = (start + stop) / 2

        valid_chrom = self.values["chrom"] == chrom
        valid_start = self.values["start"] <= stop
        valid_stop  = self.values["stop"] >= start
        valids = valid_chrom & valid_start & valid_stop

        indices = np.nonzero(valids)[0]

        if not len(indices):
            return np.zeros(0, dtype=self.values.dtype), [], []

        valid_values = self.values[indices]
        typs = ((1 + (valid_values["start"] < start)) << 2) + (2 - (valid_values["stop"] > stop))
        dists = (mid - (valid_values["start"] + valid_values["stop"]) / 2).astype(np.int64)

        return valid_values, typs, dists


    def nearest(self, chrom, start, stop, n=1):
        '''return the nearest n regions'''

        chrom = self.clear_chrom(chrom)
        start = int(start)
        stop = int(stop)

        valid_chrom = self.values["chrom"] == chrom
        valid_values = self.values[valid_chrom]

        #calculate distances
        distances_left = start - valid_values["stop"]
        distances_right = valid_values["start"] - stop
        distances = np.fmax(distances_left, distances_right)
        overlaps = distances <= 0
        distances[overlaps] = 0

        # calculate overlap_size
        max_start = np.fmax(start, valid_values["start"])
        min_stop = np.fmin(stop, valid_values["stop"])
        overlap_sizes = min_stop - max_start


#        distances[overlaps] = 0
#        overlap_sizes[np.logical_not(overlaps)] = 0

        sorted_indices = np.argsort(distances)
#        return valid_values[sorted_indices[0:n]]

        distances = distances * (valid_values["direction"] * 2 - 1) * np.sign(distances_left)

        return valid_values[sorted_indices[0:n]], distances[sorted_indices[0:n]], overlap_sizes[sorted_indices[0:n]]


    def neighbours(self, chrom, start, stop, side=True):
        chrom = self.clear_chrom(chrom)
        mid = (int(start) + int(stop)) / 2

        valid_chrom = self.values["chrom"] == chrom
        valid_values = self.values[valid_chrom]

        #calculate distances
        if side:
            ancors = np.copy(valid_values["stop"])
            directions = valid_values["direction"]
            ancors[directions] = valid_values["start"][directions]
        else:
            #use the mids as ancor points
            ancors = (valid_values["start"] + valid_values["stop"]) / 2
        distances = ancors - mid

        left_valid = distances<0
        right_valid = distances>=0

        if np.sum(left_valid):
            left_index = np.argmax(distances[left_valid])
            left_value = valid_values[left_valid][left_index]
            left_distance = distances[left_valid][left_index]
            left_distance = left_distance * (1 - 2 * directions[left_valid][left_index])
        else:
            left_value = np.empty(1, dtype=self.values.dtype)
            left_distance = 0

        if np.sum(right_valid):
            right_index = np.argmin(distances[right_valid])
            right_value = valid_values[right_valid][right_index]
            right_distance = distances[right_valid][right_index]
            right_distance = right_distance * (1 - 2 * directions[right_valid][right_index])
        else:
            right_value = np.empty(1, dtype=self.values.dtype)
            right_distance = 0

        ret_values = np.vstack((left_value, right_value))

        return append_fields(ret_values, ("distance", "overlap"), ((left_distance,right_distance), (0,0)))
