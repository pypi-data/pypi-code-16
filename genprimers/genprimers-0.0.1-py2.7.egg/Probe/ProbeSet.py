from __future__ import division
from Bio import SeqIO
from Bio.SeqUtils import GC
from Bio.SeqUtils.lcc import lcc_simp
from Bio.Seq import Seq
from ProbePair import ProbePair
from Thermo import DNAThermoModel
from Sequence import Aligner
import sys
import logging
import unittest


class ProbeSet(dict):
    """Representation of a set of Probes

    Parameters:
    -----
    probes_set: Python dict<Probes>
                Original set of probes

    probes_pairs: Python dict(Probe_ID:Probe)
                  Set of probes pairs

    pb_filtered: Python dict(String:Integer)
                 Probe filtering resume

    pp_filtered: Python dict(String:Integer)
                 Probes Pairs filtering resume

    thermo_model: DNAThermoModel class
                  Thermodynamic model used to measure energies

    n_raw_probes: Integer
                  number of probes when the ProbeSet object is initialized

    n_filt_probes: Integer
                   Number of probes after Probe filtering

    n_total_pairs: Total number of elements of the class ProbePair

    n_filt_pairs: Total number of the elements of the class ProbePair after
    probe pair filtering
    """

    def __init__(self, probes_set):
        self.probes_set = probes_set
        self.probes_pairs = None

        self.pb_filtered = {"keep": 0,
                            "n": 0,
                            "mt": 0,
                            "gc": 0,
                            "lcc": 0,
                            "ghm": 0,
                            "gss": 0}

        self.pp_filtered = {"keep": 0,
                            "frac": 0,
                            "amp": 0,
                            "int": 0}
        self.thermo_model = DNAThermoModel()

        # probe info
        self.n_raw_probes = len(probes_set)
        self.n_filt_probes = None

        # pair info
        self.n_total_pairs = 0
        self.n_filt_pairs = None

    def filter_probes(self, na, mg, op_tp, min_lcc, min_mt,
                      max_mt, min_gc, max_gc, thr_gss, thr_ghm, prim_con):
        """Filter the Probes elements contained in this class according a set
        of sequence and thermodynamics parameters

        Args:
        -----
            na: Float
                Molar concentration of Na

            mg: Float
                Molar concentration of Mg

            op_tp: Float
                   Operation temperature in C

            min_lcc: Float
                     minimum local composition complexity

            min_mt: Float
                    minimum melting temperature for probe

            max_mt: Float
                    maximium melting temperature for probe

            min_gc: Float
                    minimum gc content allowed (expressed as percentage)

            max_gc: FLoat
                    maximum gc content allowed (expressed as percentage)

            thr_gss: Float
                     Free Gibbs energy threshold for hairpin formation in
                     kcal/mol

            thr_ghm: Float
                     Free Gibbs energy threshold for homodimer formation in
                     kcal/mol

            Return:
            -------
            Void

            Notes:
            ------
            This function generates a Python dict(Probe_id:Probe) with the
            Probes that pass the filters and override the class parameter
            probes_set

        """
        logger = logging.getLogger("gp.filter.primers")
        logger.info("Filtering raw primers")
        filtered_probes = dict()

        for probe_id in self.probes_set:
            tmp_probe = self.probes_set[probe_id]

            if "N" in tmp_probe.seq:
                self.pb_filtered["n"] += 1
                continue

            gc = GC(tmp_probe.seq)
            if not (min_gc <= gc <= max_gc):
                self.pb_filtered["gc"] += 1
                continue

            lcc = lcc_simp(tmp_probe.seq)
            if lcc < min_lcc:
                self.pb_filtered["lcc"] += 1
                continue

            dghm = self.thermo_model.calc_homodimer(str(tmp_probe.seq),
                                                    na,
                                                    mg,
                                                    prim_con,
                                                    op_tp)
            if dghm < thr_ghm:
                self.pb_filtered["ghm"] += 1
                continue

            dgss = self.thermo_model.calc_hairpin(str(tmp_probe.seq),
                                                  na,
                                                  mg,
                                                  prim_con,
                                                  op_tp)
            if dgss < thr_gss:
                self.pb_filtered["gss"] += 1
                continue

            mt = self.thermo_model.calc_melting(tmp_probe.seq)
            if not (min_mt <= mt <= max_mt):
                self.pb_filtered["mt"] += 1
                continue

            self.pb_filtered["keep"] += 1
            tmp_probe.mt = round(mt, 3)
            tmp_probe.gc = round(gc, 3)
            tmp_probe.lcc = round(lcc, 3)
            tmp_probe.dghm = round(dghm, 3)
            tmp_probe.dgss = round(dgss, 3)
            filtered_probes[probe_id] = tmp_probe

        self.n_filt_probes = len(filtered_probes)
        self.probes_set = filtered_probes

        logger.info("Filtering results:")
        logger.info("  "+str(self.pb_filtered["n"])+" were filtered by" +
                    "N bases")
        logger.info("  "+str(self.pb_filtered["mt"])+" were filtered by" +
                    " melting temperature")
        logger.info("  "+str(self.pb_filtered["gc"])+" were filtered by" +
                    " GC percentage")
        logger.info("  "+str(self.pb_filtered["lcc"])+" were filtered by" +
                    " low complexity")
        logger.info("  "+str(self.pb_filtered["ghm"])+" were filtered by" +
                    " homodimer formation")
        logger.info("  "+str(self.pb_filtered["gss"])+" were filtered by" +
                    " hairpin formation")
        logger.info("  "+str(len(self.probes_set))+" raw primers were kept")

        if len(self.probes_set) == 0:
            logger.error("All raw primers were filtered, quiting..")
            sys.exit()

    def get_sdss_regions(self, op_tm, na, sdss_t, con):
        """Define the start site of the SDSS region for each probe

        Args:
        -----
        op_tm: Float
               Operation temperature in C

        na: Float
            Molar concentration of Na

        sdss_t: Float
                SDSS threshold

        con: Float
             Probe concentration

        Returns:
        --------
        Void

        Notes:
        ------
        This function uses all the instances of the class Probe stored in the
        probe_set parameter. For each probe, assign the Probe class parameter
        sdss_start
        """

        logger = logging.getLogger("gp.get.sdss")
        logger.info("Getting SDSS region for each filtered primer")
        sdss_starts = []
        for probe_id in self.probes_set:
            pb_obj = self.probes_set[probe_id]
            pb_obj.sdss_start = self.thermo_model.calc_sdss(pb_obj.seq,
                                                            f_threshold=sdss_t,
                                                            cpo=con,
                                                            temp=op_tm+273.15,
                                                            saltc=na)
            if pb_obj.sdss_start is None:
                logger.warning("SDSS could not be defined for probe " +
                               pb_obj.id)
            sdss_starts.append(pb_obj.sdss_start)
        return sdss_starts

    def assign_coords(self, fasta_indx, mm_threshold):
        """Aligns all the Probes in the set to a list of sequences

        Args:
        -----
        fasta_indx : String
                     Path of the indexed fasta with the sequences

        mm_threshold: Integer
                      Maximum number of mismatches allowed in the alignment

        Return:
        -------
        Void

        Notes:
        ------
        All the alignments for a given Probe are stored in the Probe it self
        inside of the alignments parameter
        """

        logger = logging.getLogger("gp.align.primers")
        logger.info("aligning SDSS region of each filtered primer against " +
                    " the universe of sequences")
        univ_dict = SeqIO.index(fasta_indx, "fasta")
        alignments = []
        # iterate over all the alignments between the set of probes and the
        # universe sequences
        for algn in Aligner.align_seqs(self.probes_set, fasta_indx):

            probe_id = algn[0]
            hit_id = algn[2]
            algn_start = algn[3]
            algn_strand = algn[1]

            probe_obj = self.probes_set[probe_id]

            if algn_strand == "+":
                start = int(algn_start) - probe_obj.sdss_start
                end = start + probe_obj.seq_len - 1
            else:
                start = int(algn_start)
                end = start + probe_obj.seq_len - 1

            if end >= len(univ_dict[hit_id]) or start < 0:
                continue

            if algn_strand == "+":
                hit_seq = univ_dict[hit_id][start:end+1].seq
            else:
                hit_seq = univ_dict[hit_id][start:end+1].seq
                hit_seq = hit_seq.reverse_complement()

            mm = 0
            for pos in range(0, probe_obj.seq_len):
                if probe_obj.seq[pos] != hit_seq[pos]:
                    mm += 1

            if mm <= mm_threshold:
                probe_obj.add_alignment(hit_id, start, end, algn_strand, mm)
                alignments.append((hit_id, start, end,
                                   algn_strand, mm, probe_id))
        return alignments

    def def_primers_pairs(self, targets_records, min_targets_frac,
                          min_amp_size, max_amp_size, dghm_threshold, na,
                          mg, prim_con, temp, max_pairs):
        """Defines the pairs of probes that are candidates to be Primers

        Args:
        -----
        target_records: dict(seq_id: SeqRecord)
                        dictionary of BioPython records with the target
                        sequences

        target_frac: Float
                     minimum fraction of target detected

        min_amp_size: Integer
                      Minium amplicon size

        max_amp_size: Integer
                      Maximum amplicon size

        dghm_threshold: Float
                        Free Gibbs energy threhsold in kcal/mol for homodimer
                        interaction

        na: Float
            Molar concentration for Na
        mg: Float
            Molar concentration for Mg
        prim_con: Float
                  Molar concentration of for probes
        temp: Float
              Operation temperature in C
        max_pairs: Integer
                   Maximum number of pairs reported

        Return:
        -------
        Void

        Notes:
        This function populates the class parameter probes_pairs with
        instances of the ProbePair class. These instances represent the set of
        pairs of probes that passed all the thermodynamic filters
        """

        logger = logging.getLogger("gp.primer.pairs")
        probes = self.probes_set.values()
        n_probes = len(probes)
        targets_ids = [record.id for record in targets_records]
        all_pairs = []

        logger.info("Evaluating all primers pairs")
        # compare all against all probes
        for i in range(0, n_probes-1):

            tmp_probe_a = probes[i]

            for j in range(i+1, n_probes):

                # count the number of possible pairs
                self.n_total_pairs += 1

                tmp_probe_b = probes[j]

                # create a new pair of probes
                tmp_pp = ProbePair("pair_"+tmp_probe_a.id+"_"+tmp_probe_b.id,
                                   tmp_probe_a,
                                   tmp_probe_b)

                # check if the pair is suitable for primers
                candidates = tmp_pp.are_candidates(targets_ids,
                                                   min_targets_frac,
                                                   min_amp_size, max_amp_size,
                                                   na, mg, prim_con, temp,
                                                   dghm_threshold)
                if candidates == 0:
                    self.pp_filtered["keep"] += 1
                    all_pairs.append(tmp_pp)
                elif candidates == -1:
                    self.pp_filtered["frac"] += 1
                elif candidates == -2:
                    self.pp_filtered["amp"] += 1
                else:
                    self.pp_filtered["int"] += 1

        logger.info("Pairing results:")
        logger.info("  "+str(self.pp_filtered["frac"])+" pairs were" +
                    " discarded beacuse they did not cover the minimum" +
                    " fraction of targets")
        logger.info("  "+str(self.pp_filtered["amp"])+" pairs were discarded" +
                    " because they generated weird amplicons")
        logger.info("  "+str(self.pp_filtered["int"])+" pairs were discarded" +
                    " because they were able to interact one each other")
        logger.info("  "+str(self.pp_filtered["keep"])+" pairs were kept," +
                    " but the best "+str(max_pairs)+" pairs will be reported" +
                    " due to the -r flag")

        if len(all_pairs) > 0:
            # sorted by fscore_a, fscore_b, melt_temp, dG and mean_amp_size
            pairs_sorted = sorted(all_pairs, key=lambda x: (-x.a_fscore,
                                                            -x.b_fscore,
                                                            x.met_diff,
                                                            -x.inter_energy,
                                                            x.mean_amp_len))
            # return the first max_pairs pairs
            self.probes_pairs = pairs_sorted[:max_pairs]
        else:
            logger.error("All primers pairs were discarded, quiting..")
            sys.exit()


class ProbePairUnittest(unittest.TestCase):
    """
    """

    def test_filter_probes(self):

        seqs = ["AAATCT",
                "TCTGTC",
                "AGTTAA",
                "CCGATT",
                "GGCTAT",
                "TATGCC",
                "GGTACT"]
        probes_set = dict()
        for i in range(0, len(seqs)):
            from Probes import Probe
            tmp = Probe(str(i), seqs[i])
            probes_set[str(i)] = tmp
        ps = ProbeSet(probes_set)
        self.assertEqual(ps.filter_probes(50/1e3, 0,
                                          37, 1.5, -18,
                                          -20, 30, 60,
                                          0, -2.5, 50/1e9),
                         {"n": 0, "mt": 2,
                          "gc": 2, "lcc": 1,
                          "ghm": 2, "gss": 0})

    def test_get_sdss_region(self):
        seqs = [Seq("GACGCATGCTCCTGATACTTCCAATAAT"),
                Seq("GACGCATGCTCCTGATACTTCCAATAA"),
                Seq("GACGCATGCTCCTGATACTTCCAATA"),
                Seq("GACGCATGCTCCTGATACTTCCAAT"),
                Seq("GACGCATGCTCCTGATACTTCCAA"),
                Seq("GACGCATGCTCCTGATACTTCCA"),
                Seq("CGACGCATGCTCCTGATACTTCC")]
        probes_set = dict()
        for i in range(0, len(seqs)):
            from Probes import Probe
            tmp = Probe(str(i), seqs[i])
            probes_set[str(i)] = tmp
        ps = ProbeSet(probes_set)

        self.assertEqual(ps.get_sdss_regions(60, 1, 0.01, 2e-7),
                         [12, 12, 11, 11, 10, 10, 10])

    def test_assign_coords(self):
        from Probes import Probe
        index = "/genoma/homes/ddiaz/diego_projects/mathomics_software/" +\
                "genprimers/test/sequence.fa"
        seqs = [Seq("CCTGCA"),
                Seq("ATGCATGC"),
                Seq("TTGGGGCAT")]
        probes_set = dict()
        for i in range(0, len(seqs)):
            tmp = Probe(str(i), seqs[i])
            tmp.sdss_start = 2
            probes_set[str(i)] = tmp
        ps = ProbeSet(probes_set)
        res = [("sequence1", 1, 6, "-", 1, '0'),
               ("sequence1", 13, 18, "-", 1, '0'),
               ("sequence1", 17, 22, "-", 1, '0'),
               ("sequence1", 5, 10, "-", 1, '0'),
               ("sequence1", 9, 14, "-", 1, '0'),
               ("sequence1", 11, 16, "+", 1, '0'),
               ("sequence1", 15, 20, "+", 1, '0'),
               ("sequence1", 3, 8, "+", 1, '0'),
               ("sequence1", 7, 12, "+", 1, '0'),
               ("sequence1", 10, 17, "-", 0, '1'),
               ("sequence1", 14, 21, "-", 0, '1'),
               ("sequence1", 18, 25, "-", 2, '1'),
               ("sequence1", 2, 9, "-", 0, '1'),
               ("sequence1", 6, 13, "-", 0, '1'),
               ("sequence1", 8, 15, "+", 0, '1'),
               ("sequence1", 12, 19, "+", 0, '1'),
               ("sequence1", 16, 23, "+", 0, '1'),
               ("sequence1", 0, 7, "+", 0, '1'),
               ("sequence1", 4, 11, "+", 0, '1')]
        self.assertEqual(ps.assign_coords(index, 2), res)
