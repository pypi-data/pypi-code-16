from collections import defaultdict
from Bio.Seq import Seq
import unittest


class Probe:
    """Representation of a Probe

    Parameters:
    -----------
        id : String
             probe identifier

        seq : Bio.Seq object
              Probe sequence

        seq_len: Integer
                 Length of the Probe sequence

        alignments: Python dict(seq_id:[[start,end]..])
                    Coordinates where the Probe can align

        mt: Float
            melting temperature in C

        gc: Float
            GC percentage

        lcc: Float
             Local composition complexity (sequence entropy, in terms of the
             information theory)

        dghm: Float
              Free Gibbs energy for homodimer formation in kcal/mol

        dgss: Float
              Free Gibbs energy for hairpin formation in kcal/mol

        sdss_start: Integer
              Position in the sequence where the SDSS starts

        Notes:
        ------
        A probe is a sequence of DNA or RNA. It the probe is able to meet some
        sequence and thermodynamics parameters, then it is a candidate to be a
        Primer
        """

    def __init__(self, id, sequence):
        self.id = id
        self.seq = sequence
        self.seq_len = len(sequence)
        self.alignments = defaultdict(list)
        self.mt = None
        self.gc = None
        self.lcc = None
        self.dghm = None
        self.dgss = None
        self.sdss_start = None

    def add_alignment(self, seq_id, start, end, strand, mm):
        """Adds a new place where this probe can align in a set of sequences

        Args:
        -----
        seq_id: String
                identifier of the hit sequence

        start: Integer
               start position of the match in the hit sequence

        end: Integer
             end position of the match in the hit sequence

        strand: String (+ or -)
            strand where the probe aligned in the hit sequence

        mm: Integer
            number of mistmaches in the alignment

        Notes:
        ------
        The alignments positions must be zero-based
        """

        if start >= end:
            raise ValueError("alignment start greater than end")
        elif ((end - start) + 1) != self.seq_len:
            raise ValueError("alignment size greater than sequence length")
        elif strand != "+" and strand != "-":
            raise ValueError("%s is not an valid strand" % strand)
        elif mm >= self.seq_len:
            raise ValueError("Number of mismatches grater than sequence" +
                             + " length (%s:%d > %s:%d)" % (seq_id, mm,
                                                            self.id,
                                                            self.seq_len))

        else:
            self.alignments[seq_id].append((start, end, strand, mm))

    def to_fasta(self, add_info=True, sdss=False):
        """Transforms the Probe to FASTA format

        Args:
        -----
        add_info: Booleans
                  Boolean to add Probe info in the FASTA header
        sdss: Boolean
              Boolean to print only the SDSS region in the FASTA

        Return:
        -------
        String: the String representation of the Probe
        """
        if add_info:
            fasta = ">"+self.id +\
                    " melt_tmp="+str(self.mt) +\
                    " gc_cont="+str(self.gc) +\
                    " lcc="+str(self.lcc) +\
                    " dghm="+str(self.dghm) +\
                    " dgss="+str(self.dgss)+"\n"
        else:
            fasta = ">"+self.id+"\n"
        flag = True
        bg = 0
        end = 80

        if sdss and self.sdss_start is not None:
            seq_to_print = self.seq[self.sdss_start:]
            seq_to_print_len = len(seq_to_print)
        else:
            seq_to_print = self.seq
            seq_to_print_len = self.seq_len

        while flag:
            if end > seq_to_print_len:
                end = seq_to_print_len
                flag = False
            if flag:
                fasta += str(seq_to_print[bg:end])+"\n"
            else:
                fasta += str(seq_to_print[bg:end])
            bg = end
            end = bg + 80
        return fasta

    def get_alignments(self, seq_id, by_strand=False):
        """Returns the alignments for this Probe

        Args:
        -----
        seq_id: String
                Identifier of the sequence where the probe was aligned
        by_strand: Boolean
                   If true, then return the alignments of the probe in the
                   seq_id sequence in a list of 2 lists [[],[]].  The first
                   list contains all the alignments in the + strand and the
                   second list the alignments in the - strand
        Return:
        -------
        List: List with the alignments

        Notes:
        ------
        Each alignment is in the form [start, end]. Where start and end are
        the positions of the alignment
        """

        # get all the alignments of this probe with the seq_id sequence
        alignments = self.alignments[seq_id]

        # return None if there are no aligments with the seq_id sequence
        if len(alignments) == 0:
            return None

        if by_strand:
            # sort by alignments by strand and then by position
            alignments = sorted(alignments, key=lambda x: (x[2], x[0]))

            # split the alignments in two lists according in which strand of
            # the sequence the probe aligned
            pos_aligns = []
            neg_aligns = []
            for align in alignments:
                if align[2] == "+":
                    pos_aligns.append(align)
                else:
                    neg_aligns.append(align)

            return (pos_aligns, neg_aligns)

        else:
            return alignments

    def get_hits_list(self):
        """Returns the list of sequences where the probe could be aligned on
        """
        return self.alignments.keys()

    def to_tsv(self):
        """Returns the info of the Probe class in form of TSV info
        """
        return "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (self.id,
                                                   self.seq,
                                                   str(self.mt),
                                                   str(self.gc),
                                                   str(self.lcc),
                                                   str(self.dghm),
                                                   str(self.dgss),
                                                   str(self.sdss_start))


class ProbesUnittest(unittest.TestCase):
    """
    unittesting for Probes
    """

    def test_add_alinments(self):
        pb = Probe("id", "ATCGATTACGAT")
        with self.assertRaises(ValueError):
            pb.add_alignment("hit1", 14, 10, "+", 3)
            pb.add_alignment("hit2", 5, 25, "+", 4)
            pb.add_alignment("hit3", 9, 12, "p", 6)
            pb.add_alignment("hit4", 12, 25, "+", 13)

    def test_get_alignments(self):
        pb = Probe("id", "ATCGATTACGAT")
        pb.add_alignment("hit1", 1, 12, "+", 3)
        pb.add_alignment("hit4", 13, 24, "+", 3)
        pb.add_alignment("hit4", 25, 36, "-", 3)
        self.assertEqual(pb.get_alignments("hit5"), None)
        self.assertEqual(pb.get_alignments("hit1"), [(1, 12, "+", 3)])
        self.assertEqual(pb.get_alignments("hit1", by_strand=True),
                         ([(1, 12, "+", 3)], []))
        self.assertEqual(pb.get_alignments("hit4"), [(13, 24, "+", 3),
                                                     (25, 36, "-", 3)])
        self.assertEqual(pb.get_alignments("hit4", by_strand=True),
                         ([(13, 24, "+", 3)],
                          [(25, 36, "-", 3)]))

    def test_to_fasta(self):
        pb = Probe("id", "ATCGATTACG")
        pb.sdss_start = 3
        self.assertEqual(pb.to_fasta(),
                         '>id melt_tmp=None gc_cont=None' +
                         ' lcc=None dghm=None dgss=None\nATCGATTACG')
        self.assertEqual(pb.to_fasta(add_info=False),
                         '>id\nATCGATTACG')
        self.assertEqual(pb.to_fasta(sdss=True),
                         '>id melt_tmp=None gc_cont=None' +
                         ' lcc=None dghm=None dgss=None\nGATTACG')
        self.assertEqual(pb.to_fasta(add_info=False, sdss=True),
                         '>id\nGATTACG')

    def test_to_tsv(self):
        pb = Probe("id", "ATCGATTACG")
        self.assertEqual(pb.to_tsv(), "id\tATCGATTACG\tNone" +
                                      "\tNone\tNone\tNone\tNone\tNone")
