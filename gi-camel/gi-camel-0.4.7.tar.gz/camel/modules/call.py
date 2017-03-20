#call all meth informations for each cpg

import pysam
import time
import sys
import h5py
import argparse
import numpy as np
import math
import os

from bisect import bisect_left
from collections import defaultdict, namedtuple
from itertools import islice

Hit = namedtuple("Hit", "typ, rel_pos, qual, index")

def get_positions(left, right, gc):
    #perform a bidirectional search for gc positions
    pos = bisect_left(gc, left)
#    pos = np.searchsorted(gc, left)

    while pos < len(gc) and gc[pos] <= right:
        yield (gc[pos], pos)
        pos += 1

def get_hits(read, positions):
    #ignore last position on forward and last position on reverse
    hit_positions = get_positions(read.pos + 1, read.aend - 1, positions[read.tid])
    seq = read.seq.upper()

    for pos, index in hit_positions:
        rel_pos = relative_pos(read, pos-1)

        if (rel_pos == None):
            continue

        pair_orientation = read.is_read1 == read.is_reverse

        rel_pos += pair_orientation
        rel_next_pos =  rel_pos + 1 - pair_orientation * 2

        try:
            char = seq[rel_pos]
            next_char = seq[rel_next_pos]
        except:
            print("error", read.qname, read.pos, read.cigar, hit_positions, file=sys.stderr)
            continue

        if pair_orientation and char == 'A' and next_char == 'C':
            typ = 3
        elif not pair_orientation and char == 'C' and next_char == 'G':
            typ = 0
        elif pair_orientation and char == 'G' and next_char == 'C':
            typ = 2
        elif not pair_orientation and char == 'T' and next_char == 'G':
            typ = 1
        elif pair_orientation and next_char == "T":
            typ = 5
        elif not pair_orientation and next_char == "A":
            typ = 4
        else:
            # SNPs
            typ = -1

        ref = "C" if not pair_orientation else "G"

        if rel_pos >= 0:
            yield Hit(typ, rel_pos, ord(read.qual[rel_pos]), index)


def get_hits_nome(read, positions):
    #ignore last position on forward and last position on reverse
    hit_positions = get_positions(read.pos + 1, read.aend - 1, positions[read.tid])

    seq = read.seq.upper()

    for pos, index in hit_positions:
        rel_pos = relative_pos(read, pos-1)

        if (rel_pos == None):
            continue

        pair_orientation = read.is_read1 == read.is_reverse

        rel_pos += 1 - pair_orientation #dirty hack

        try:
            char = seq[rel_pos]
        except:
            print("error", read.qname, read.pos, read.cigar, hit_positions, file=sys.stderr)
            continue

        if not pair_orientation and char == 'T':
            typ = 3
        elif pair_orientation and char == 'G':
            typ = 0
        elif not pair_orientation and char == 'C':
            typ = 2
        elif pair_orientation and char == 'A':
            typ = 1
        else:
            # SNPs
            typ = -1

        if rel_pos >= 0:
            yield Hit(typ, rel_pos, ord(read.qual[rel_pos]), index)


def check_files_exists(*filenames):
    # check filenames
    for f in filenames:
        if not os.path.isfile(f):
            raise Exception("{} not found".format(f))


def run(args):
    bam_filename = args.input
    index_filename = args.index
    output_filename = args.output
    mbq = args.mbq
    mmq = args.mmq
    max_snp_fraction = args.max_snp_fraction


    check_files_exists(index_filename, bam_filename)

    samfile = pysam.Samfile(bam_filename, "r")

    print("load index", file=sys.stderr)
    index = h5py.File(index_filename, 'r')

    print("create datastructures", file=sys.stderr)

    #check if cpg_positions exist / correct index
    for r in index:
        if not "cpg_positions" in index[r]:
            raise Exeption("cpg_positions missing in {}. Please call camel index to create a valid camel-index-file".format(index_filename))
        if args.nome and not "gpc_positions" in index[r]:
            raise Exeption("cpg_positions missing in {}. Please call camel index with --nome param to create a valid camel-index-file for nome calling".format(index_filename))


    # init datastructures
    cpg_positions = [index[r]["cpg_positions"][:].tolist() if r in index else None for r in samfile.references]
    cpg_ctga = [np.zeros((len(index[r]["cpg_positions"]),6), dtype=np.int) if r in index else None for r in samfile.references]


    # init nome datastructures
    gpc_ctga = None
    if args.nome:
        gpc_positions = [index[r]["gpc_positions"][:].tolist() if r in index else None for r in samfile.references]
        gpc_ctga = [np.zeros((len(index[r]["gpc_positions"]),6), dtype=np.int) if r in index else None for r in samfile.references]

#    imprinting_count = dict((samfile.gettid(c), np.zeros((len(index[c]["cpg_positions"]),4), dtype=np.int)) for c in chromosomes)

#    per_pos_stats = [[]] * 101
#    for i in range(len(per_pos_stats)):
#        per_pos_stats[i] = [0,0]

#    count = 0
    timestart = time.time() #measure running time

    print("open samfile", file=sys.stderr)

    samout = args.samout
    ignore_duplicates = args.ignore_duplicates

    if samout:
        #pipethrough header
        print("sam output activated", file=sys.stderr)
        outfile = pysam.AlignmentFile("-", "wh", header=samfile.header)

    if ignore_duplicates:
        from camel.helper.bloomfilter import Bloomfilter, calculate_bloomfilter_size
        # calculate bloomfilter params
        bitcount, hash_function_count = calculate_bloomfilter_size(args.read_count, args.error_rate)
        print("create bloomfilter for duplicate filtering ({bitcount} bits, {hashcount} hash functions)".format(bitcount=bitcount, hashcount=hash_function_count), file=sys.stderr)
        bf = Bloomfilter(bitcount, hash_function_count)

    camel_duplicates = set()
    mark_duplicates = set()

    for count, read in enumerate(samfile):
        if samout:
            #pipethrough reads
            outfile.write(read)

        if count % 1000000 == 0:
            print(count, "reads processed", file=sys.stderr)
#            if count == 1000000: break

        # filter out duplicates and unmapped reads

        if read.is_duplicate or read.mapq < mmq or not cpg_positions[read.tid] or read.is_unmapped:
            continue

        def read_key(read):
            '''return the positioning key for an read used for duplication detection'''
            if read.is_reverse:
                return (read.next_reference_id, read.next_reference_start, read.isize)
            else:
                return (read.reference_id, read.reference_start, read.isize)

        def check_dup():
            pos = read_key(read)
            is_seen = bf.lookup(pos)
            bf.add(pos)
            return is_seen

        is_duplicate = None

        #TODO: use read.get_reference_positions?

        # for each cpg position on the read
        for h in get_hits(read, cpg_positions):
            #perform duplication check (only if there are hits
            if ignore_duplicates and is_duplicate is None:
                is_duplicate = check_dup()
            if is_duplicate:
                break

            # add only if minumum quality is reached
            if h.qual < mbq or h.typ == -1: continue
            # handle duplicate checks
            cpg_ctga[read.tid][h.index, h.typ] += 1

        # nome calling
        if args.nome:
            #perform duplication check (only if there are hits
            if ignore_duplicates and is_duplicate is None:
                is_duplicate = check_dup()
            if is_duplicate:
                break

            # for each gpc position on the read
            for h in get_hits_nome(read, gpc_positions):
                # add only if minumum quality is reached
                if h.qual < mbq or h.typ == -1: continue
                gpc_ctga[read.tid][h.index, h.typ] += 1

    if samout:
        outfile.close()


    #            if prev_h:
    #                imprinting_typ = ((h.typ & 1) << 1) + (prev_h.typ & 1)
    #                imprinting_count[read.tid][h.index, imprinting_typ] += 1
    #            prev_h = h


    def remove_snps(values_ctga, max_snp_fraction=0.2):
        for x in values_ctga:
            if x is None:
                continue
            first_coverage = np.sum(x[:,(2,3,5)], axis=1)
            first_coverage[first_coverage==0] = -1
            first_ratio = x[:,5] / first_coverage

            second_coverage = np.sum(x[:,(0,1,4)], axis=1)
            second_coverage[second_coverage==0] = -1
            second_ratio = x[:,4] / second_coverage

            select = (first_ratio > max_snp_fraction) & (x[:,5] >= 2) | (second_ratio > max_snp_fraction) & (x[:,4] >= 2)
            rselect = np.repeat(select, 6).reshape((-1,6))
            x[rselect] = 0


    print("removing c->t snps", file=sys.stderr)
    remove_snps(cpg_ctga, max_snp_fraction)

    print("removing g->a snps (NOMe)", file=sys.stderr)
    if args.nome:
        remove_snps(gpc_ctga, max_snp_fraction)

    print(time.time() - timestart, "seconds for calling", file=sys.stderr)


    # saving all data
    save(output_filename, samfile, cpg_ctga, gpc_ctga) #imprinting_count=imprinting_count

    print(time.time() - timestart, "seconds", file=sys.stderr)


def save(output_filename, samfile, cpg_ctga, gpc_ctga, imprinting_count=None):
    #save hdf5 file
    out_file = h5py.File(output_filename, 'w')

    #writing cpg_positions
    for tid in range(len(cpg_ctga)):
        if cpg_ctga[tid] is None: continue
        chrom       = samfile.getrname(tid)
        grp         = out_file.create_group(chrom)
        data_methyl = cpg_ctga[tid][:,0:4]
        print("writing", samfile.getrname(tid), data_methyl.shape, file=sys.stderr)
        dset        = grp.create_dataset("methylation", dtype='i', data=data_methyl, maxshape=data_methyl.shape)

        if imprinting_count:
            data_imprinting = imprinting_count[tid]
            dset = grp.create_dataset("imprinting", dtype='i', data=data_imprinting, maxshape=data_imprinting.shape)

    if gpc_ctga:
        #writing gpc_positions
        for tid in range(len(gpc_ctga)):
            if gpc_ctga[tid] is None: continue
            chrom       = samfile.getrname(tid)
            grp         = out_file[chrom]
            data_methyl = gpc_ctga[tid][:,0:4]
            print("writing", samfile.getrname(tid), data_methyl.shape, file=sys.stderr)
            dset        = grp.create_dataset("nome", dtype='i', data=data_methyl, maxshape=data_methyl.shape)

    out_file.close()


def relative_pos(read, pos):
    # calculate the position of the base, without deletions and insertions
    relative_pos = pos - read.pos
    cigar        = read.cigar
    curr_pos     = 0

    for c in cigar:
        if curr_pos + c[1] <= relative_pos:
            if c[0] == 2 or c[0] == 4: #deletion or soft clipping
                relative_pos -= c[1]
            if c[0] == 1: #insertion
                relative_pos += c[1]
            else: #match
                curr_pos += c[1]
        else:
            if c[0] == 2: #cpg inside deletion
                return None
            else:
                return relative_pos
    return None


def sub(parser):
    parser.add_argument('input',help='The input bam file.')
    parser.add_argument('index', help='The camel-index-file.')
    parser.add_argument('output', help='The output camel-data file.')
    parser.add_argument('-mbq', nargs='?', help='minimum pred-scaled base quality score', default=17, type=int)
    parser.add_argument('-mmq', nargs='?', help='minimum pred-scaled mapping quality score', default=30, type=int)
    parser.add_argument('--nome', '-n', action='store_true', help='perform an additional nome calling')
    parser.add_argument('--samout', '-s', action='store_true', help='print sam to stdout')
    parser.add_argument('--ignore-duplicates', '-d', action='store_true', help='Activate the ignore-duplication mode to perform own pcr-duplication detection by read positions using a bloomfilter. The setup of the bloomfilter requires an aproximate read-count and an error-rate. Note that the default value requires 3.35GB of memory.')
    parser.add_argument('--read-count', '-r', metavar="N", nargs='?', help='Set the input read count, used for size determination of the bloomfilter (default: 1000000000). Only needed in ignore-duplication mode', default=1000000000, type=int)
    parser.add_argument('--error-rate', '-e', metavar="N", nargs='?', help='Set the error-rate, used for size determination of the bloomfilter (default: 0.00001). Only needed in ignore-duplication mode.', default=0.0001, type=float)
    parser.add_argument('--max_snp_fraction', "-f", help="Set the maximum fraction of basepairs to not discard a CpG as SNP. (CpGs with a snp fraction higher than this values get discarded)", default=0.2, type=int)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate methylation level for each CpG.')
    sub(parser)
    args = parser.parse_args()
    run(args)
