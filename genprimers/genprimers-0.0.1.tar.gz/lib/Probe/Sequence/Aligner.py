from subprocess import Popen
from subprocess import PIPE
from tempfile import mkdtemp
from os.path import join
from os import devnull
from shutil import rmtree


def align_seqs(probes, indexed_fasta):
    """given a set of instances of the class Probe, yields the alignments of these
    probes against a set of sequences

    Args:
    -----
    probes: Python dict(probe_id:Probe)
            instances of the Probe class
    indexed_fasta: String
                   Path of the indexed fasta file containing the sequeces to
                   align with sequence

    Note:
    -----
    For the moment, this function is a wrapper to run bowtie. I would be
    better to implement these method using (maybe) an FM-index of the fasta
    sequence, and allowing some mismatching in the backward search of the BWT
    """

    tmp_dir = mkdtemp()
    tmp_fasta = join(tmp_dir, "probes.fasta")
    fasta_handler = open(tmp_fasta, 'w')

    for probe_id in probes:
        fasta_handler.write(probes[probe_id].to_fasta(add_info=False,
                                                      sdss=True)+"\n")

    fasta_handler.close()

    bowtie_cmd = "bowtie -v 0 -f -k 80 --suppress 5,6,7 "+indexed_fasta +\
                 " "+tmp_fasta + "| sort -k1,1 -k2,2 | sed 's/:.>.//g'"

    with open(devnull, 'w') as dn:
        bowtie_proc = Popen(bowtie_cmd, shell=True, stdout=PIPE, stderr=dn)

    for align in bowtie_proc.stdout:
        align = align.rstrip("\n")
        align_vect = align.split("\t")
        yield align_vect
    rmtree(tmp_dir)
