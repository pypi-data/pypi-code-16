import numpy as np
import h5py
from collections import namedtuple
from os.path import basename, splitext

from camel.helper.common import savitzky_golay

class Sample:
    def __init__(self, filename):
        self.filename = filename
        self.basename = basename(splitext(filename)[0])
        self.f = h5py.File(filename, 'r')

        self.duplication_rate = self.value("meta/duplication_percentage")
        self.lambda_meth = self.value("meta/lambda_meth")
        self.all_meth = self.value("meta/all_meth")
        self.examined_pairs = self.value("meta/examined_pairs")
        self.unpaired_reads = self.value("meta/unpaired_reads")
        self.unmapped = self.value("meta/unmapped_reads")
        self.lane_count = self.value("meta/lanecount")
        self.convertion_rate = 1 - self.lambda_meth if self.lambda_meth is not None else None
        self.read_coverage = self.value("meta/coverage")


        #TODO: check if unmapped_reads are already counted in examined_reads by markduplicates
        if self.unmapped and self.examined_pairs and self.unpaired_reads:
            self.efficiency = 1 - self.unmapped / (self.examined_pairs * 2 + self.unpaired_reads + self.unmapped)
        else:
            self.efficiency = None

    def chromosomes(self):
        return [c for c in self.f]


    def value(self, path):
        if path in self.f:
            return self.f[path][0]
        return None


    def methylation(self, chrom, start_index=None, stop_index=None, nome=False):

        if not nome:
            values = self.f[chrom]["methylation"]
        else:
            values = self.f[chrom]["nome"]

        if start_index and stop_index:
            return values[start_index:stop_index]

        return values[:]


    def _methylated(self, value_matrix):
        '''return the count of the methylated reads of a value matrix'''
        return np.sum(value_matrix[:,(0,2)], axis=1)


    def _coverage(self, value_matrix):
        '''return the coverage of a value matrix'''
        return np.sum(value_matrix, axis=1)


    def methylated(self, chrom, start_index=None, stop_index=None):
        return self._methylated(self.methylation(chrom))


    def coverage(self, chrom, start_index=None, stop_index=None):
        return self._coverage(self.methylation(chrom))


    def m_values(self, chrom, start_index=None, stop_index=None, min_cov=0, smooth_window=0):
        values = self.methylation(chrom, start_index, stop_index)
        coverage = self._coverage(values)
        methylated = self._methylated(values)

        coverage[coverage == 0] = 1 #prevent division by zero afterwards
        m_values = methylated / coverage

        if smooth_window > 0:
            m_values = savitzky_golay(m_values, smooth_window)

        if min_cov > 0:
            m_values = m_values[coverage > min_cov]

        return m_values


    def __repr__(self):
        return self.basename


    def __lt__(self, other):
        return self.basename < other.basename
