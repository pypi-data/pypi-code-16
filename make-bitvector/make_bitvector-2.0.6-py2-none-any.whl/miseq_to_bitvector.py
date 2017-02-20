import pysam
import numpy as np
import pandas as pd
import multiprocessing
import time 
from alignedRead import Read
from helper import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def display(message, verbose):
	''' If the option is set to verbose, displays the message
	'''
	if verbose:
		print message
	return None

def miseq_to_bitvector(inFile, outFile, ref_trim, quals=True, use_deletions=False, nreads=np.inf, use_multiprocessing=True, strict_overlap=False, save_reads=None, verbose=False):
	'''
	Generates a bit vector with for the target gene in the region of interest and saves bitvector to outFile.

	@param: inFile - String which is the input sam/bam file 
	@param: outFile - String which is the output file name
	@param: ref_trim - Boolean mapping the target gene to target region, gene: [start,stop) 
	@param: quals - Boolean which is True if you want to consider quality of sequenced positions
	@param: use_deletions - Boolean which is True if you want to consider deletions as mutations
	@param: nreads - maximum number of lines to read
	@param: multiprocessing - Boolean which is true if we should use multiple processors
	@param: strict_overlap - Boolean which is true iff we want both reads to completely overlap in the region of interest
	@param: save_reads - a tuple containing the coordinates such that if a read overlaps these coordinates, the read is saved. None if save no reads.

	@return: dataframe containing bit vectors, titled outFile.
	'''
	sam = pysam.AlignmentFile(inFile,'r')
	ref_lengths = dict(zip(sam.references,sam.lengths))
	sam.close()

	print 'Collecting matching pairs of reads aligning to the region of interest...'
	pair1, pair2, unpaired_read_count, read_positions = collect_pairs(inFile, ref_trim, nreads, strict_overlap, save_reads, verbose)
	
	print 'Processing %d pairs of reads...' %len(pair1)
	if not use_multiprocessing: # do not use multiprocessing
		bitvectors = generate_bitvectors(pair1, pair2, ref_trim, ref_lengths, use_deletions, quals)

	if use_multiprocessing: #use multiprocessing
		nprocess = multiprocessing.cpu_count()
		mprocesses = []
		pool = multiprocessing.Pool(processes=nprocess)
		
		subpair_size = len(pair1)/(nprocess)+1
		print( 'Creating bitvectors in parallel with {0} processes'.format(nprocess))
		# Break lists into sublists for parallel processing 
		for its in xrange(nprocess):
			subpair1 = pair1[subpair_size*its:min(subpair_size*(its+1),len(pair1))]
			subpair2 = pair2[subpair_size*its:min(subpair_size*(its+1),len(pair2))]
			mprocesses.append(pool.apply_async(generate_bitvectors,args=(subpair1, subpair2, ref_trim, ref_lengths),kwds=dict(use_deletions=use_deletions, quals=quals)))
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

	print 'Saving output file ...'
	bitvectors.to_csv(outFile, sep=" ")
	print 'Done.'

	return bitvectors

def plot_amplified_regions(read_positions):
	'''
	'''

def collect_pairs(inFile, ref_trim, nreads, strict_overlap, save_reads, verbose):  
	'''
	Given a Miseq aligned sam/bam file, this method collects reads and their corresponding pairs
	which align to a reference within a start and end frame.
	'''
	sam = pysam.AlignmentFile(inFile,'r')
	
	reference = ref_trim.keys()[0]
	ref_start = ref_trim[reference][0]
	ref_end = ref_trim[reference][1] 
	
	# Initialize list containing corresponding pairs of reads.
	pair1 = []
	pair2 = []
	
	# Keep track of unpaired reads
	unpaired_read_count  = 0
	
	i = 0   # initialize count to get read1
	read1, read2 = None, None   
	num_pairs = 0

	read_starts = {}
	read_ends = {}

	coverage = {}

	softclip = 0
	def is_softclipped(read):
		matches = 0
		clips = 0
		for (op, count) in read.cigartuples:
			if op == 4:
				clips += count
			if op == 0:
				matches += count

		if matches < 100:
			return True
		return False

	for read in sam:
		if i%2 == 0: 
			read1 = read
			i += 1    #Got read1, next time, grab read2
			continue

		## Catch read2 this time ##
		
		#Ensure successive reads are proper pairs
		if read.query_name != read1.query_name:      # if read does not match previous read, then discard, start afresh and grab a read2 next time
			read1 = read
			i = 1     # got read1, next time, grab read2
			if read1.reference_name == reference:
				unpaired_read_count += 1
			continue

		read2 = read
		i = 0     # got read2, next time, grab read1
		num_pairs += 1

		# grab two paired reads and compare them
		try:
			assert read1.query_name == read2.query_name
		except AssertionError:
			if verbose:
				print('Unpaired reads slipped through filter')
		try:
			assert read1.reference_name == read2.reference_name #Paired reads must be from the same reference
			# Remove reads with the wrong reference
			if read1.reference_name != reference:
				continue #Ignore reads which do not align to the desired reference.
				
		except AssertionError:
			if verbose:
				print('Paired reads align to different references: %s and %s \t %s \t %s \t %s' % (read1.reference_name,read2.reference_name, read1.query_name, read1.reference_start, read2.reference_start))
			continue

		if is_softclipped(read1) or is_softclipped(read2):
			softclip += 1
			continue

		try:
			coverage[(read1.reference_start, read2.reference_start, read1.reference_end, read2.reference_end)] += 1
		except KeyError:
			coverage[(read1.reference_start, read2.reference_start, read1.reference_end, read2.reference_end)]  = 1

		# Ignore read pairs if neither read aligns to the desired region on the reference.
		if ((read1.reference_start > ref_end or read1.reference_end < ref_start) and 
			(read2.reference_start > ref_end or read2.reference_end < ref_start) ):
			continue
		
		if strict_overlap:
			#Ensure that both reads entirely cover the region of interest
			if not (read1.reference_start <= ref_start and read1.reference_end >= ref_end and read2.reference_start<=ref_start and read2.reference_end>=ref_end):
				continue


		pair1.append(Read(read1))
		pair2.append(Read(read2))

		if num_pairs > nreads:
			break

	sam.close()

	plt.figure()
	ax1 = plt.gca()
	rects = []
	for key in coverage:
		(r1_start, r2_start, r1_stop, r2_stop) = key
		count = coverage[key]
		start = max(r1_stop, r2_stop) 
		stop = min(r1_start, r2_start)
		width = stop - start
		uncovered_start = min(r1_stop, r2_stop) 
		uncovered_stop = max(r1_start, r2_start)
		uncovered_width = uncovered_stop - uncovered_start
		rects.append((count, start, width, uncovered_start, uncovered_width))

	rects.sort(key=lambda x: x[2])

	running_count = 0
	for (count, start, width, uncovered_start, uncovered_width) in rects:
		ax1.add_patch(Rectangle((start - .1, running_count - .1), width, count, linewidth=0, alpha=1))
		if uncovered_width > 0:
			ax1.add_patch(Rectangle((uncovered_start - .1, running_count - .1), uncovered_width, count, linewidth=0, alpha=1, hatch="/", color="slategrey"))
		running_count += count

	plt.title('Read coverage in gene of interest')

	# recompute the ax.dataLim
	ax1.relim()
	# update ax.viewLim using the new dataLim
	ax1.autoscale_view()
	plt.draw()
	plt.savefig(inFile[:-4]+'coverage.eps')

	return (pair1, pair2, unpaired_read_count, coverage)

	
def combine_pair_xor(read1, read2, ref_trim, ref_lengths, use_deletions, quals, verbose=False):
	'''
	Return a bitvector which is the bitvector in agreement between two paired reads.
	@param: read1 - 
	@param: read2 - 

	'''
	out1 = parse_read(read1,ref_trim,ref_lengths,use_deletions,quals)
	out2 = parse_read(read2,ref_trim,ref_lengths,use_deletions,quals)

	nan_vals = np.intersect1d(np.argwhere(np.isnan(out1)), np.argwhere(np.isnan(out2)))
	combined = np.logical_and(out1,out2).astype(np.int)
	combined[nan_vals] = 0
	n_muts = np.nansum(combined)
	combined = combined.astype(np.str)
	combined[nan_vals] = '?'
	return (''.join(combined), n_muts)
	
def generate_bitvectors(pair1, pair2, ref_trim, ref_lengths, use_deletions=False, quals=True, verbose=False):
	'''
	Generate bitvectors from two lists of Miseq reads, where pair1[i] is the corresponding read for pair2[i].
	Mutations are denoted by a '1', non-mutations by a '0' and poor quality positions by '?'
	A mutation is valid only if it occurs in both read, where there is overlap.
	
	@param: pair1 - list of Miseq reads. Each read is a pysam AlignedRead object
	@param: pair2 - list of Miseq reads. Each read is a pysam AlignedRead object. Must be the same length as read1
	@param: use_deletions - a boolean which is True iff deletions should be considered as mutations
	@param: quals - a boolean which is True iff the quality of bases should be considered 
	
	@return: a dataframe containing the query name, bit vector, number of mutatons, reference name, start position 
	'''
	
	bitvectors = {'Query_name':[], 'Binary_vector':[], 'N_mutations':[], 'Reference_name':[], 'Start_position':[]}
	# Ensure lists are of equal length
	assert len(pair1) == len(pair2)
	for read_count in range(len(pair1)):
		read1 = pair1[read_count]
		read2 = pair2[read_count]
		
		# Ensure both reads come from the same reference 
		assert read1.reference_name == read2.reference_name
		(bitvector, n_muts) = combine_pair_xor(read1, read2, ref_trim, ref_lengths, use_deletions, quals)

		bitvectors['Query_name'].append(read1.query_name)
		bitvectors['Binary_vector'].append(bitvector)
		bitvectors['N_mutations'].append(n_muts)
		bitvectors['Reference_name'].append(read1.reference_name)
		bitvectors['Start_position'].append(ref_trim[read1.reference_name][0])
	
	bitvectors = pd.DataFrame(bitvectors, columns=['Query_name','Binary_vector','N_mutations','Reference_name', 'Start_position'])
	return bitvectors


def test():
	inFile = 'test_files/170117Rou_D17-802Jan2017l2.sam'
	outFile = 'test_files/hiseq_test'
	print 'Testing'
	miseq_to_bitvector(inFile, outFile, ref_trim={'HIV':[455,855]}, use_multiprocessing=True)

##------------------------------------------------------------DEPRECATED------------------------------------------------------------##

def combine_pair(read1, read2, ref_trim, use_deletions=False, quals=True, verbose=False):
	'''
	
	'''
	#    
#        # Find region of overlap
#        overlap = True
#        if read2.reference_start >= read1.reference_end-1 or read1.reference_start >= read2.reference_end-1:
#            overlap = False
#        else:
#            overlap_start = max(read1.reference_start, read2.reference_start) # Find the position where overlap begins
#            overlap_end = min(read1.reference_end-1, read2.reference_end-1) # Find the position where overlap ends
#            overlap = True
#
#        if not overlap: 
#            continue
#        
#        if verbose:     # if we want to display overlap information 
#            print read1.reference_start, read1.reference_end-1, read2.reference_start, read2.reference_end-1, overlap
#            if overlap:
#                print >> sys.stderr, 'Overlap: ', overlap_start, overlap_end
#
#        # Parse MD strings and obtain positions of mutations (relative to read start)    
#        read1_muts, read1_dels = get_positions(read1.get_tag('MD'), use_deletions)
#        read2_muts, read2_dels = get_positions(read2.get_tag('MD'), use_deletions)
#
#        val_pos_1 =  combine_quals(read1, read1_dels, use_deletions) # list of (pos, qual)
#        val_pos_2 =  combine_quals(read2, read2_dels, use_deletions) # list of (pos, qual)
#
#        # Get list of bad quality positions, relative to genome
#        discard_pos_1 = [e[0] + read1.reference_start for e in val_pos_1 if e[1] < 20]
#        discard_pos_2 = [e[0] + read2.reference_start for e in val_pos_2 if e[1] < 20]
#
#        # Get list of good positions, relative to genome 
#
#        bad_pos = set(discard_pos_1 + discard_pos_2)
#        all_val_pos =  set( [e[0] + read1.reference_start for e in val_pos_1 if e[1] >= 20] + [e[0] + read2.reference_start for e in val_pos_2 if e[1] >= 20] ) 
#
#        # Collect good quality positions and their corresponding bases, relative to genome
#
#        read1_pos = [e[1] + read1.reference_start for e in read1_muts if e[1] not in discard_pos_1]
#        read2_pos = [e[1] + read2.reference_start for e in read2_muts if e[1] not in discard_pos_2]
#
#        read1_bases = [e[0] for e in read1_muts if e[1] + read1.reference_start not in discard_pos_1]
#        read2_bases = [e[0] for e in read2_muts if e[1] + read2.reference_start not in discard_pos_2]
#
#        all_muts = set(read1_pos + read2_pos)   # A list of all valid mutations
#
#        muts = np.zeros(ref_lengths[read.reference_name])
#        output = np.asarray(['?']*ref_lengths[read.reference_name])
#
#        for pos in all_val_pos:
#            output[pos] = '0'
#
#        for mut in all_muts:
#            if overlap: 
#            ## if regions overlap, select which mutations to accept
#            ## Mutations in overlapping regions must be validly covered by both reads, otherwise the poor-quality 
#            ## read is not allowed to report on it
#
#                if (overlap_start <= mut <= overlap_end) and not (mut in discard_pos_1 or mut in discard_pos_2): 
#                    
#                    ## The mutation is validly covered by both reads, so it must be present in both, otherwise discarded
#                    if mut in read1_pos and mut in read2_pos:
#                        # mutation present is present in both
#                        output[mut] = '1'
#                        muts[mut] = 1
#                else:
#                    # The mutation is not validly covered by both reads, so we accept it as trustworthy
#                    output[mut] = '1'
#                    muts[mut] = 1
#
#        for pos in bad_pos:
#            if output[pos] != '1':
#                output[pos] = '?'
#
#        if ref_trim != None:
#            output = output[ref_trim[read.reference_name][0]:ref_trim[read.reference_name][1]]
#            muts = muts[ref_trim[read.reference_name][0]:ref_trim[read.reference_name][1]]
#        output[mask_index] = '?'
#        muts[mask_index] = 0
#        n_muts = np.nansum(muts)
#        if verbose:
#            if random.random() < 0.000001:
#                print >> sys.stderr, read1.reference_start, read2.reference_start, read1_pos, read2_pos, bad_pos
#                print >> sys.stderr, output
#                
#        # Add this bitvector to the pandas array.
#        if set(output) != {'?'}:
#            bitvector.loc[num_pairs-1] = [read.query_name, ''.join(output), n_muts, read.reference_name]
#            
#        if set(output) != {'?'} and n_muts>1: 
#            outF.write(read.query_name+' '+''.join(output)+' '+str(n_muts)+' '+read.reference_name+'\n')
#            
#        if num_pairs >= nline: break
#    
#    # Close all resources.
#    sam.close()
#    outF.close()
#    
#    return bitvector
	pass








