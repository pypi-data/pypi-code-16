import h5py, sys
import numpy as np
import argparse

def sub(parser):
	parser.add_argument('index', help='the index')
	parser.add_argument('input', help='the hdf5 methylation file')
	parser.add_argument('cpgs', help='the cpg hdf5 file')


def run(args):
	f = h5py.File(args.input)
	index = h5py.File(args.index)
	fc = h5py.File(args.cpgs)

	all_cov = 0
	all_length = 0

	for chrom in map(str, range(1,23)):
		arr = f[chrom]['methylation']
		arr_cpg = fc[chrom]["positions"]
		arr_ind = index[chrom]["cpg_positions"]

		cpg_ind = np.searchsorted(arr_ind, arr_cpg)

		for start, stop in cpg_ind:
			cpg_islang_cov = np.sum(arr[start:stop])
			all_cov += cpg_islang_cov
			all_length += stop-start

	print(all_cov / all_length)


#		print(chrom, round(all_sum / arr.shape[0], 2), sep='\t')


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	sub(parser)
	args = parser.parse_args()
	run(args)
