import pysam
import numpy as np
import pandas as pd
import multiprocessing
import time 
from alignedRead import Read
from helper import *

def hiseq_to_bitvector(inFile, outFile, ref_trim, quals=True, use_deletions = False, nreads = np.inf, use_multiprocessing=True, strict_overlap=False, save_reads=None, verbose=False):
	'''
	Generates a bit vector with for the target gene in the region of interest and saves bitvector to outFile.

	@param: inFile - String which is the input sam/bam file 
	@param: outFile - String which is the output file name
	@param: ref_trim - Boolean mapping the target gene to target region, gene: [start,stop) 
	@param: quals - Boolean which is True if you want to consider quality of sequenced positions
	@param: use_deletions - Boolean which is True if you want to consider deletions as mutations
	@param: nreads - maximum number of lines to read
	@param: multiprocessing - Boolean which is true if we should use multiple processors
	@param: strict_overlap - Boolean which is true iff we want the read to completely cover the region of interest
	@param: save_reads - a tuple containing the coordinates such that if a read overlaps these coordinates, the read is saved. None if save no reads.
	@return: dataframe containing bit vectors, titled outFile.
	'''

	sam = pysam.AlignmentFile(inFile,'r') 
	ref_lengths = dict(zip(sam.references,sam.lengths))


	reference = ref_trim.keys()[0]
	ref_start = ref_trim[reference][0]
	ref_stop = ref_trim[reference][1]

	print 'Collecting reads aligned to region of interest...'
	reads, read_positions = collect_reads(inFile, nreads, reference, ref_start, ref_stop, strict_overlap, verbose)
	print 'Processing %d reads...' %len(reads)
	
	if not use_multiprocessing: # do not use multiprocessing
		bitvectors = generate_bitvectors(reads, ref_trim, ref_lengths, quals, use_deletions)

	if use_multiprocessing: #use multiprocessing
		nprocess = multiprocessing.cpu_count()
		mprocesses = []
		pool = multiprocessing.Pool(processes=nprocess)
		
		subreads_size = len(reads)/(nprocess)+1
		print( 'Creating bitvectors in parallel with {0} processes'.format(nprocess))
		# Break lists into sublists for parallel processing 
		for its in xrange(nprocess):
			subreads = reads[subreads_size*its:min(subreads_size*(its+1),len(reads))]
			mprocesses.append(pool.apply_async(generate_bitvectors,args=(subreads, ref_trim, ref_lengths),kwds=dict(use_deletions=use_deletions, quals=quals)))
		pool.close()
		# Wait for results
		print( 'Waiting for results...')
		pool.join()
		print( 'Done with multiprocessing. Fetching results...')
		frames = []
		for its, process in enumerate(mprocesses):
			df = process.get()
			frames.append(df)
		bitvectors = pd.concat(frames, ignore_index = True)

	#save file as outFile
	print 'Saving results...'
	bitvectors.to_csv(outFile, sep=" ")
	print 'Done.'
	return bitvectors

def collect_reads(inFile, nreads, reference, ref_start, ref_stop, strict_overlap):
	'''
	Collects all the relevant reads corresponding to a region of interest, and outputs a list containing the reads.
	@param: inFile - the name of the input sam/bam file
	@param: nreads - the maximum number of reads to allow
	@param: reference -  the name of the reference gene 
	@param: ref_start - the start (inclusive) of the region of interest
	@param: ref_stop - the end (exclusive) of the region of interest
	@param: strict_overlap - Boolean which is true iff we want the read to completely cover the region of interest
	
	@output:
		None
	'''
	sam = pysam.AlignmentFile(inFile,'rb')

	all_reads = []

	processed_reads = 0
	read_starts ={}
	read_ends = {}

	for read in sam:
		# Remove bad reads
		if read.is_unmapped: continue
		if read.reference_name != reference: continue

		#Keep track of the region being amplified
		read_starts[read.reference_start] += read_starts.get(read.reference_start,0) + 1
		read_ends[read.reference_end] += read_ends.get(read.reference_end,0) + 1

		# ignore read if it doesn't overlap with the trimmed region
		if read.reference_start > ref_stop or read.reference_end < ref_stop: continue

		if strict_overlap:
			# Only allow reads that completely cover the region of interest
			if not (read.reference_start <= ref_start and read.reference_end>= ref_stop):
				continue

		all_reads.append(Read(read))
		processed_reads += 1
		if processed_reads > nreads: break

	read_positions = {'starts':read_starts, 'ends':read_ends}
	sam.close()
	return all_reads, read_positions


def generate_bitvectors(reads, ref_trim, ref_lengths, quals, use_deletions):
	'''
	'''
	
	bitvectors = {'Query_name':[], 'Binary_vector':[], 'N_mutations':[], 'Reference_name':[], 'Start_position':[]}

	for read in reads:
		bitvector = parse_read(read, ref_trim, ref_lengths, use_deletions, quals)
		n_muts = 0 if np.isnan(np.nansum(bitvector)) else int(np.nansum(bitvector))
		nan_vals = np.argwhere(np.isnan(bitvector))
		
		bitvector = bitvector.astype(np.int).astype(np.str)
		bitvector[nan_vals] = '?'
		bitvector = ''.join(bitvector)

		bitvectors['Query_name'].append(read.query_name)
		bitvectors['Binary_vector'].append(bitvector)
		bitvectors['N_mutations'].append(n_muts)
		bitvectors['Reference_name'].append(read.reference_name)
		bitvectors['Start_position'].append(ref_trim[read.reference_name][0])
	
	bitvectors = pd.DataFrame(bitvectors, columns=['Query_name','Binary_vector','N_mutations','Reference_name', 'Start_position'])
	return bitvectors