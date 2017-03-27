from __future__ import division
from NNModel import NNModel
import re
from math import e
from math import pow
from Bio.Seq import Seq
from math import log
from primer3 import calcHairpin
from primer3 import calcHomodimer
from primer3 import calcHeterodimer
from Bio.SeqUtils import MeltingTemp
import unittest


def _count_overlapping(subseq, seq):
    """Counts the number of overlapping occurrences of a given subsequences
    Args:
    -----
    seq: BioPython Seq
         Sequence to be scanned
    subseq: String
            Subsequence to be searched
    Returns:
    Integer: the number of overlapping ocurrences
    """
    return len(re.findall(r'(?=(%s))' % re.escape(subseq), seq))


class DNAThermoModel(NNModel):
    """Represents the DNA Thermodynamic model to calculate energies

    Notes:
    ------
        Use dictionaries to store the NN data so that there's no
        confusion about which value belongs to which NN pair.
        Units of energy are kcal/mole.  Units of entropy are are "e.u",
        or cal/mol/K.  Need to divide by 1000 before multiplying by T

    Parameters:
    -----------
        dh: Python dict()
            enthalpy data from SantaLucia and Hicks, Annu. Rev. Biophys.
            Biomol. Struc 2004

        ds: Python dict()
            entropy data from SantaLucia and Hicks, Annu. Rev. Biophys.
            Biomol. Struc 2004

        dg: Python dict()
            Gibbs free energy data from SantaLucia and Hicks, Annu. Rev.
            Biophys. Biomol. Struc 2004

        init_dh: Float
                 initial correction for enthalpy

        init_ds: Float
                 initial correction for entropy

        init_dg: Float
                 initial correction for Gibbs free energy

        sym_ds:  Float
                 symetry correction for entropy

        sym_dg: Float
                symetry correction for Gibbs free energy

        end_dh: Float
                terminal AT penalty for enthalpy

        end_ds: Float
                terminal AT penalty for entropy

        end_dg: Float
                terminal AT penalty for Gibbs free energy

        dangle5_dh: Python dict()
                    5' dangling corrections for enthalpy

        dangle5_ds: Python dict()
                    5' dangling corrections for entropy

        dangle5_dg: Python dict()
                    5' dangling corrections for Gibbs free energy

        dangle3_dh: Python dict()
                    3' dangling corrections for enthalpy

        dangle3_ds: Python dict()
                    3' dangling corrections for entropy

        dangle3_dg: Python dict()
                    3' dangling corrections for Gibbs free energy

    """
    def __init__(self):
        NNModel.__init__(self)

        self.dh = {'AA': -7.6, 'AT': -7.2, 'AC': -8.4, 'AG': -7.8,
                   'TA': -7.2, 'TT': -7.6, 'TC': -8.2, 'TG': -8.5,
                   'CA': -8.5, 'CT': -7.8, 'CC': -8.0, 'CG': -10.6,
                   'GA': -8.2, 'GT': -8.4, 'GC': -9.8, 'GG': -8.0}

        self.ds = {'AA': -21.3, 'AT': -20.4, 'AC': -22.4, 'AG': -21.0,
                   'TA': -21.3, 'TT': -21.3, 'TC': -22.2, 'TG': -22.7,
                   'CA': -22.7, 'CT': -21.0, 'CC': -19.9, 'CG': -27.2,
                   'GA': -22.2, 'GT': -22.4, 'GC': -24.4, 'GG': -19.9}

        self.dg = {'AA': -1.00, 'AT': -0.88, 'AC': -1.44, 'AG': -1.28,
                   'TA': -0.58, 'TT': -1.00, 'TC': -1.30, 'TG': -1.45,
                   'CA': -1.45, 'CT': -1.28, 'CC': -1.84, 'CG': -2.17,
                   'GA': -1.30, 'GT': -1.44, 'GC': -2.24, 'GG': -1.84}

        # initiation correction
        self.init_dh = 0.2
        self.init_ds = -5.7
        self.init_dg = 1.96

        # symmetry correction
        self.sym_ds = -1.4
        self.sym_dg = 0.43

        # terminal AT penalty
        self.end_dh = 2.2
        self.end_ds = 6.9
        self.end_dg = 0.05

        # 5' dangling end corrections. First base is dangling
        self.dangle5_dh = {'AA': +0.2, 'CA': +0.6, 'GA': -1.1, 'TA': -6.9,
                           'AC': -6.3, 'CC': -4.4, 'GC': -5.1, 'TC': -4.0,
                           'AG': -3.7, 'CG': -4.0, 'GG': -3.9, 'TG': -4.9,
                           'AT': -2.9, 'CT': -4.1, 'GT': -4.2, 'TT': -0.2}

        self.dangle5_dg = {'AA': -0.51, 'CA': -0.42, 'GA': -0.62, 'TA': -0.71,
                           'AC': -0.96, 'CC': -0.52, 'GC': -0.72, 'TC': -0.58,
                           'AG': -0.58, 'CG': -0.34, 'GG': -0.56, 'TG': -0.61,
                           'AT': -0.50, 'CT': -0.02, 'GT': +0.48, 'TT': -0.10}

        self.dangle5_ds = {k: ((self.dangle5_dh[k] - self.dangle5_dg[k]) /
                               self.Tref) for k in self.pairs}

        # 3' dangling end corrections. Second base is dangling
        self.dangle3_dh = {'AA': -0.5, 'AC': +4.7, 'AG': -4.1, 'AT': -3.8,
                           'CA': -5.9, 'CC': -2.6, 'CG': -3.2, 'CT': -5.2,
                           'GA': -2.1, 'GC': -0.2, 'GG': -3.9, 'GT': -4.4,
                           'TA': -0.7, 'TC': +4.4, 'TG': -1.6, 'TT': +2.9}

        self.dangle3_dg = {'AA': -0.12, 'AC': +0.28, 'AG': -0.01, 'AT': -0.13,
                           'CA': -0.82, 'CC': -0.31, 'CG': -0.01, 'CT': -0.52,
                           'GA': -0.92, 'GC': -0.23, 'GG': -0.44, 'GT': -0.35,
                           'TA': -0.48, 'TC': -0.19, 'TG': -0.50, 'TT': -0.29}

        self.dangle3_ds = {k: ((self.dangle3_dh[k] - self.dangle3_dg[k]) /
                               self.Tref) for k in self.pairs}

    def calc_energies(self, s, T=37+273.15, saltc=None):
        """Calculates thermodynamic parameters of a DNA duplex

        Notes
        -----
        Uses nearest-neighbor model to calculate enthalpy, entropy,
        and free-energy of duplex formation, using nearest-neighbor
        parameters from [1]_.  Includes corrections for symmetry,
        dangling ends, and AT termination, but does not (yet) include
        loop corrections or corrections for mismatches.  Therefore it
        implicitly assumes that there are no mismatches.
        cseq, if specified, is used only to determine dangling-end
        corrections.  The function does *not* check if it is actually
        complementary.
        .. [1] SantaLucia and Hicks, Annu. Rev. Biophys. Biomol. Struct.
           2004.

        Args:
        -----
        s : BioPython Seq object
            duplex of interest
        T : float, optional
            Temperature (in K) at which to calculate Delta_G.  Default
            is 37 C (310.15 K)
        saltc : float, optional
            Concentration of monovalent salt, in mol/L (default: 1 M)

        Returns
        -------
        dH, dS, dG : tuple of float
            Delta_H, Delta_S, Delta_G of hybridization, in kcal/mol
            for dH and dG and kcal/mol/K for dS

        """

        dH = dS = 0
        cs = s.reverse_complement()

        # apply dangling end corrections first
        if str(s) != str(cs.reverse_complement()):
            if s.startswith('-'):
                # add a 3' dangling end correction
                pair = str(cs[-2:])
                dH += self.dangle3_dh[pair]
                dS += self.dangle3_ds[pair]
            if cs.startswith('-'):
                # add a 3' dangling end correction
                pair = str(s[-2:])
                dH += self.dangle3_dh[pair]
                dS += self.dangle3_ds[pair]
                # trim sequence to avoid overcounting pairs
                s = s[0:-1]
            if s.endswith('-'):
                # add a 5' dangling end correction
                pair = str(cs[:2])
                dH += self.dangle5_dh[pair]
                dS += self.dangle5_ds[pair]
            if cs.endswith('-'):
                # add a 5' dangling end correction
                pair = str(s[:2])
                dH += self.dangle5_dh[pair]
                dS += self.dangle5_ds[pair]
                # trim sequence to avoid overcounting pairs
                s = s[1:]

        # use dictionary comprehension to count total number of each NN pair
        nncounts = {pair: _count_overlapping(pair, str(s)) for pair
                    in self.pairs}

        dH += sum(nncounts[pair]*self.dh[pair] for pair in self.pairs)
        dS += sum(nncounts[pair]*self.ds[pair] for pair in self.pairs)

        # apply symmetry correction if sequence is self-complementary
        if str(s) == str(s.reverse_complement()):
            dS += self.sym_ds

        # apply end corrections
        if (s.startswith('A') or s.startswith('T')):
            dH += self.end_dh
            dS += self.end_ds

        if (s.endswith('A') or s.endswith('T')):
            dH += self.end_dh
            dS += self.end_ds

        # apply initiation correction
        dH += self.init_dh
        dS += self.init_ds

        # apply salt correction
        # this implicitly assumes there is no 5' terminal phosphate, as is
        # usually the case for synthetic oligonucleotides
        if saltc:
            dS = dS + (0.368*(len(s)-1)*log(saltc))

        # apply temperature correction; assuming dCp = 0
        dG = dH - T*dS/1000

        return dH, dS/1000, dG

    def calc_melting(self, seq):
        """Calculates the melting temperature for a given sequence
        Args:
        -----
        seq : BioPython Seq object

        Returns:
        --------
        Float: melting temperature

        Notes:
        ------
        Uses the function MeltingTemp from the package Bio.SeqUtils
        """
        return MeltingTemp.Tm_NN(seq)

    def calc_homodimer(self, seq, na, mg, c, temp):
        """ Calculates the Gibbs free energy for Homodimer formation in a DNA
        sequence

        Args:
        -----
        seq: BioPython Seq object
             Sequence to be evaluated

        na: Float
            Na concentration in Molar

        mg: Float
            Mg concentration in Molar

        c: Float
            Sequence concentration in Molar

        temp: Float
              Operation temperature in C

        Returns:
        --------
        Float: Gibbs free energy

        Notes:
        ------
        This module uses the function calcHomodimer from the primer3 python
        module. The results are in Kcal/mol

        """
        return calcHomodimer(seq,
                             mv_conc=na*1000,
                             dv_conc=mg*1000,
                             dna_conc=c*1e9,
                             temp_c=temp).dg/1000

    def calc_heterodimer(self, seq1, seq2, na, mg, c, temp):
        """Calculates the Gibbs free energy for Heterodimers formation between
        two DNA sequences

        Args:
        -----
        seq1: BioPython Seq object
             Sequence to be evaluated

        seq2: BioPython Seq object
              Sequence which seq1 is compared to

        na: Float
            Na concentration in Molar

        mg: Float
            Mg concentration in Molar

        c: Float
            Sequence concentration in Molar

        temp: Float
              Operation temperature in C

        Returns:
        --------
        Float: Gibbs free energy

        Notes:
        ------
        This module uses the function calcHomodimer from the primer3 python
        module. The results are in Kcal/mol
        """
        return calcHeterodimer(seq1, seq2,
                               mv_conc=na*1000, dv_conc=mg*1000,
                               temp_c=temp,
                               dna_conc=c*1e9).dg/1000

    def calc_hairpin(self, seq, na, mg, c, temp):
        """ Calculates the Gibbs free energy for Hairpin formation for a given
        DNA sequence

        Args:
        -----
        seq: BioPython Seq object
             Sequence to be evaluated

        na: Float
            Na concentration in Molar

        mg: Float
            Mg concentration in Molar

        c: Float
            Sequence concentration in Molar

        temp: Float
              Operation temperature in C

        Returns:
        --------
        Float: Gibbs free energy

        Notes:
        ------
        This module uses the function calcHomodimer from the primer3 python
        module. The results are in Kcal/mol
        """
        return calcHairpin(seq,
                           mv_conc=na*1000,
                           dv_conc=mg*1000,
                           temp_c=temp,
                           dna_conc=c*1e9).dg/1000

    def calc_sdss(self, dna_seq, f_threshold=0.01, cpo=2e-7, temp=37+273.15,
                  saltc=None):
        """Calculates the position in a DNA sequence where the SDSS start

        Args:
        -----
        dna_seq: BioPython sequence
                 DNA sequence to be evaluated
        f_threshold: Float
                 SDSS threshold
        cpu: Float
             DNA concentration
        temp: Float
              Temperature of the model
        Returns:
        --------
        Integer: Position where the SDSS start in the dna_seq

        Notes:
        ------
        This method is an implementation of the method proposed
        by Fumihito Miura in  "A novel strategy to design highly specific PCR
        primers based on the stability and uniqueness of 30-end subsequences",
        Bioinformatics, 2005
        """

        dna_len = len(dna_seq)

        for pos in reversed(range(0, dna_len-1)):
            three_prim_subseq = dna_seq[pos:]
            dH, dS, dG = self.calc_energies(three_prim_subseq, temp, saltc)

            # This is from the original code from the paper of the SDSS
            # method. I think it is a kind of cheat
            dS *= -1
            dH *= -1
            dG = dH - temp*dS
            #####

            K_as = pow(e, (dG / (self.R * temp)))
            f = (cpo * K_as) / (1 + (cpo * K_as))
            if f >= f_threshold:
                return pos
        return None


class DNAThermoModelUnittest(unittest.TestCase):

    def test_calc_energies(self):
        dmodel = DNAThermoModel()
        self.assertEqual(dmodel.calc_energies(Seq('GTCTACC')),
                         (-47.8, -0.1349, -5.960764999999995))
        # a sequence with 1 end correction
        self.assertEqual(dmodel.calc_energies(Seq('GTCTACCA')),
                         (-54.09999999999999, -0.1507, -7.36039499999999))
        # a self-complementary sequence
        self.assertEqual(dmodel.calc_energies(Seq('GTCTAGAC')),
                         (-55.79999999999999, -0.1596, -6.300059999999995))
        # a self-complementary sequence with 2 end corrections
        self.assertEqual(dmodel.calc_energies(Seq('TGTCTAGACA')),
                         (-68.39999999999999, -0.19119999999999998,
                          -9.099319999999999))
        # with salt correction to 0.5 M
        self.assertEqual(dmodel.calc_energies(Seq('GTCTACC'), saltc=0.5),
                         (-47.8, -0.13643046897467637, -5.486090047504128))

    def test_calc_melting(self):
        dmodel = DNAThermoModel()
        self.assertEqual(dmodel.calc_melting(Seq('GTCTACC')),
                         -3.9650586677994397)

    def test_calc_homodimer(self):
        dmodel = DNAThermoModel()
        self.assertEqual(dmodel.calc_homodimer('GTCTACC',
                                               50/1e3, 0, 2/1e9, 37),
                         -0.3060264978145642)

    def test_calc_heterodimer(self):
        dmodel = DNAThermoModel()
        self.assertEqual(dmodel.calc_heterodimer('GTCTACC', 'ATCTAGG',
                                                 50/1e3, 0, 2/1e9, 37),
                         -1.1131764978176615)

    def test_calc_hairpin(self):
        dmodel = DNAThermoModel()
        self.assertEqual(dmodel.calc_hairpin('GTCTACC',
                                             50/1e3, 0, 2/1e9, 37),
                         0.0)

    def test_get_sdss_region(self):
        dmodel = DNAThermoModel()
        seqs = [Seq("GACGCATGCTCCTGATACTTCCAATAAT"),
                Seq("GACGCATGCTCCTGATACTTCCAATAA"),
                Seq("GACGCATGCTCCTGATACTTCCAATA"),
                Seq("GACGCATGCTCCTGATACTTCCAAT"),
                Seq("GACGCATGCTCCTGATACTTCCAA"),
                Seq("GACGCATGCTCCTGATACTTCCA"),
                Seq("CGACGCATGCTCCTGATACTTCC")]
        starts = [12, 12, 11, 11, 10, 10, 10]
        for i in range(0, len(seqs)):
            self.assertEqual(dmodel.calc_sdss(seqs[i],
                                              temp=60+273.15,
                                              saltc=1),
                             starts[i])
