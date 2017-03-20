import argparse, re, sys
import struct
import h5py
import numpy as np


def sub(parser):
    parser.add_argument('fasta', help='the reference file in fasta format')
    parser.add_argument('--nome', action='store_true', help='do additional gcp indexing for nome-seq')
    parser.add_argument('output', help='the output index hdf5 file')


def run(args):
    print("Creating index for calling", file=sys.stderr)

    fasta, output = args.fasta, args.output
    nome = args.nome
    base_pos = 0
    chrom = ""

    fasta = open(fasta)
    index = h5py.File(output, 'w')

    line = fasta.readline()

    while True:
        if not line: #eof -> write file and end the loop
            write_hdf5(index, chrom, cpg_positions, gpc_positions, c_counts, g_counts, valid_cpg_c, valid_cpg_g, valid_gpc_g, valid_gpc_c, nome)
            break

        if line.startswith(">"): #new chrom
            if chrom:
                write_hdf5(index, chrom, cpg_positions, gpc_positions, c_counts, g_counts, valid_cpg_c, valid_cpg_g, valid_gpc_g, valid_gpc_c, nome)

            # clear the cpg_positions
            cpg_positions = [] # the cpg_positions
            gpc_positions = [] # the cpg_positions
            c_counts  = []
            g_counts  = []
            curr_c_count = 0
            curr_g_count = 0
            valid_cpg_c = []
            valid_cpg_g = []
            valid_gpc_g = []
            valid_gpc_c = []

            chrom = line.split()[0][1:] # set new chrom name
            print("Chromosome", chrom, file=sys.stderr) # output for debugging

            base_pos = 0 # begin with new base position for couting
            line = fasta.readline()
            continue

        # no new chrom
        # as long as there is an C or G at the end of the line
        # it is possible that the linebreak splits a CG
        nextline = fasta.readline()

        while (line.upper().endswith("C\n") or line.upper().endswith("G\n")) and not nextline.startswith(">"): # the \n garanties that still a line is available
            line = line.rstrip() + nextline #append next line
            nextline = fasta.readline()

        line = line.upper() # in the case the fasta file contains lower case bp

        last_start = 0
        for m in re.finditer("CG", line):
            cpg_positions.append(base_pos + m.start() + 1)
            curr_c_count += line.count("C", last_start, m.start() + 2)
            curr_g_count += line.count("G", last_start, m.start() + 2)
            c_counts.append(curr_c_count)
            g_counts.append(curr_g_count)
            last_start = m.start() + 2

            if nome:
                valid_cpg_g.append(m.start() == len(line) - 2 or not line[m.start() + 2] == "C") #CGC
                valid_cpg_c.append(m.start() == 0 or not line[m.start() -1] == "G") #GCG

        if nome:
            # GC indexing for nome-sequencing
            for m in re.finditer("GC", line):
                gpc_positions.append(base_pos + m.start() + 1)
                valid_gpc_c.append(m.start() == len(line) - 2 or not line[m.start() + 2] == "G") #GCG
                valid_gpc_g.append(m.start() == 0 or not line[m.start() -1] == "C") #CGC

        curr_c_count += line.count("C", last_start, len(line))
        curr_g_count += line.count("G", last_start, len(line))

        base_pos += len(line) - 1 # adjust base position
        line = nextline

    fasta.close()
    index.close()


def write_hdf5(index, chrom, cpg_positions, gpc_positions, c_counts, g_counts, valid_cpg_c, valid_cpg_g, valid_gpc_g, valid_gpc_c, nome=False,):
    gc_counts = np.transpose(np.array([c_counts, g_counts]))
    grp_chrom = index.create_group(chrom)
    grp_chrom.create_dataset("cpg_positions", dtype='i', data=np.array(cpg_positions), maxshape=(len(cpg_positions),))
    grp_chrom.create_dataset("gc_counts", dtype='i', data=gc_counts, maxshape=gc_counts.shape)
    if nome:
        grp_chrom.create_dataset("gpc_positions", dtype='i', data=np.array(gpc_positions), maxshape=(len(gpc_positions),))
        valid_cpg_c = np.array(valid_cpg_c, dtype=np.bool_)
        valid_cpg_g = np.array(valid_cpg_g, dtype=np.bool_)
        valid_cpg = np.vstack((valid_cpg_c,valid_cpg_g)).T

        valid_gpc_c = np.array(valid_gpc_c, dtype=np.bool_)
        valid_gpc_g = np.array(valid_gpc_g, dtype=np.bool_)
        valid_gpc = np.vstack((valid_gpc_g, valid_gpc_c)).T

        grp_chrom.create_dataset("valid_cpg", dtype=np.bool_, data=valid_cpg, maxshape=valid_cpg.shape)
        grp_chrom.create_dataset("valid_gpc", dtype=np.bool_, data=valid_gpc, maxshape=valid_gpc.shape)


def main():
    parser = argparse.ArgumentParser()
    sub(parser)
    args = parser.parse_args()
    run(args)

if __name__ == '__main__':
    main()
