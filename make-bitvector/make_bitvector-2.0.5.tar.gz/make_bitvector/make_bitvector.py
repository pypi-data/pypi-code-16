import sys
sys.path.append('..')

import argparse
from .hiseq_to_bitvector import *
from .miseq_to_bitvector import *

def convert_to_bitvector(inFile, outFile, paired, ref_trim, quals, use_deletions, nreads, use_multiprocessing=True, strict_overlap=False, verbose=False):
	if paired: # parse as a Miseq (paired read) file
		return miseq_to_bitvector(inFile, outFile, ref_trim, quals, use_deletions, nreads, use_multiprocessing, strict_overlap, verbose)
	else: # parse as a Miseq (unpaired read) file
		return hiseq_to_bitvector(inFile, outFile, ref_trim, quals, use_deletions, nreads, use_multiprocessing, strict_overlap, verbose)

def main():
	parser = argparse.ArgumentParser(description='Convert aligned DMS-modified reads to bitvectors')

	parser.add_argument('-f','--input_file',type=str,dest='inFile', required=True,
	help='File containing aligned reads to be converted to bitvectors')

	parser.add_argument('-p','--paired',type=int,dest='paired', required=True,
	help='Select "0" to parse as a Hiseq (unpaired reads) file, or "1" to parse as Miseq (paired read) file for paired reads. Reads must be sorted by pairs for a Miseq file.')


	parser.add_argument('-r','--reference',type=str,dest='reference', required=True,
		help='Enter the name of the gene/reference under consideration.')


	parser.add_argument('-c','--coord',type=str,dest='ref_coord',required=True,
	help='Start (inclusive) and end (exclusive) positions of region of interest, delimited by comma, eg 500,600')    

	parser.add_argument('-q','--quals',type=int,dest='quals',default=1,
	help='Enter 0 if you do not want to consider quality of bases (default : 1)')    

	strict_parser= parser.add_mutually_exclusive_group(required=False)
	strict_parser.add_argument('-so','--overlap', dest='strict_overlap', action='store_true')
	parser.set_defaults(strict_overlap=False)

	parser.add_argument('-d','--deletions',type=int,dest='use_deletions',default=0,
	help='Enter 1 if you want the program to consider deletions as mutations (default : 0)') 

	parser.add_argument('-o','--output_file',type=str,dest='outFile',default=None,
		help='Name of the bit-vector file if one is created. If not specified, the name of the bam file is used.')

	parser.add_argument('-m','--multiprocessing',type=int,dest='use_multiprocessing',default=1,
	help='Enter 1 to use multiprocessing to speed up code, or 0 for no parallelization (default : 1)')

	parser.add_argument('-s','--shell',type=int,dest='shell',default=0,
		help='Enter 1 to display output to shell (default : 0)')

	parser.add_argument('-n','--nreads',type=int,dest='nreads',default=np.inf,
	help='Maximum number of reads to analyse. (default : infinity)')

	parser.add_argument('-v','--verbose',type=int,dest='verbose',default=0,
	help='Enter 1 to output extra details to shell. (default : 0)')


	args = parser.parse_args()
	print(args)

	#--------------------------------------------- Variables conversion ----------------------------------
	inFile = args.inFile
	paired = args.paired
	reference = args.reference
	ref_coord = args.ref_coord
	outFile = args.outFile
	quals = args.quals
	use_deletions = args.use_deletions
	use_multiprocessing = args.use_multiprocessing
	nreads = args.nreads
	verbose = args.verbose
	strict_overlap = args.strict_overlap

	refs = [reference]
	[start, stop] = [int(y) for y in ref_coord.split(',')]

	ref_trim = {reference:[start,stop]}

	if outFile is None:
		outFile = '{0}_{1}_{2}-{3}_bitvector.txt'.format(inFile[:-4],reference,start,stop)

	bitvectors = convert_to_bitvector(inFile, outFile, paired, ref_trim, quals, use_deletions, nreads, use_multiprocessing, strict_overlap, verbose)


	if args.shell:
		print bitvectors.to_csv(sep="\t")