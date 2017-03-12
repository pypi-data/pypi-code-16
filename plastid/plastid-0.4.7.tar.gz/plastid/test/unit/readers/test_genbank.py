#!/usr/bin/env python

from nose.tools import assert_equal
from plastid.readers.genbank import GenbankReader, GenbankTranscriptAssembler
from plastid.genomics.roitools import GenomicSegment, SegmentChain, Transcript

from pkg_resources import resource_filename, cleanup_resources


gbfile = resource_filename("plastid","test/data/annotations/4cds.gb"),


class TestGenbankReader:
    
    @classmethod
    def setUpClass(cls):
        cls.expected_chains = [
            SegmentChain(GenomicSegment('NC_007194.1',0,4918979,'+'),chromosome='1',db_xref='taxon:330879',mol_type='genomic DNA',organism='Aspergillus fumigatus Af293',strain='Af293'),
            SegmentChain(GenomicSegment('NC_007194.1',215,836,'+'),codon_start='1',db_xref=['GI:146322305', 'GeneID:3507995'],locus_tag='AFUA_1G00100',note='encoded by transcript AFUA_1G00100A',old_locus_tag='Afu1g00100',product='MFS monocarboxylate transporter',protein_id='XP_001481690.1'),
            SegmentChain(GenomicSegment('NC_007194.1',3951,4253,'+'),GenomicSegment('NC_007194.1',4773,4963,'+'),codon_start='1',db_xref=['GI:70989828', 'GeneID:3507996'],locus_tag='AFUA_1G00110',note='encoded by transcript AFUA_1G00110A',old_locus_tag='Afu1g00110',product='hypothetical protein',protein_id='XP_749763.1'),
            SegmentChain(GenomicSegment('NC_007194.1',6804,6881,'-'),GenomicSegment('NC_007194.1',6899,7127,'-'),GenomicSegment('NC_007194.1',7261,7472,'-'),codon_start='1',db_xref=['GI:70989830', 'GeneID:3507997'],locus_tag='AFUA_1G00120',note='encoded by transcript AFUA_1G00120A',old_locus_tag='Afu1g00120',product='hypothetical protein',protein_id='XP_749764.1'),
            SegmentChain(GenomicSegment('NC_007194.1',36278,37475,'-'),codon_start='1',db_xref=['GI:70989846', 'GeneID:3508018'],locus_tag='AFUA_1G00200',note='encoded by transcript AFUA_1G00200A; similar to Ankyrin 1; Erythrocyte ankyrin; Ankyrin R (Swiss-Prot:P16157) [Homo sapiens]',old_locus_tag='Afu1g00200',product='F-box domain and ankyrin repeat protein',protein_id='XP_749772.1'),                                   
        ]
        cls.found_chains = [
        ]
    
    @classmethod
    def tearDownClass(cls):
        pass

    def test_attributes_match_expected(self):
        pass
    
    def test_features_match_expected(self):
        pass
    
    def test_feature_types_match_expected(self):
        pass

    def test_yields_stopfeature_on_seqchange(self):
        pass
    
    
    
class TestGenbankTranscriptAssembler:
    
    @classmethod
    def setUpClass(cls):
        pass
    
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_assembles_transcripts_from_cds(self):
        pass
    
    def test_assembles_transcripts_from_cds_and_mrna(self):
        pass

    def test_adds_three_for_stop(self):
        pass
    
    def test_works_with_multi_genbank(self):
        pass
    
    
    

#         seq = SeqIO.read(open(ANNOTATION_FILES["genbank"]),"genbank")
#         features = seq.features
#         expected_chains = [
            SegmentChain(GenomicSegment('NC_007194.1',0,4918979,'+'),chromosome='1',db_xref='taxon:330879',mol_type='genomic DNA',organism='Aspergillus fumigatus Af293',strain='Af293'),
            SegmentChain(GenomicSegment('NC_007194.1',215,836,'+'),codon_start='1',db_xref=['GI:146322305', 'GeneID:3507995'],locus_tag='AFUA_1G00100',note='encoded by transcript AFUA_1G00100A',old_locus_tag='Afu1g00100',product='MFS monocarboxylate transporter',protein_id='XP_001481690.1'),
            SegmentChain(GenomicSegment('NC_007194.1',3951,4253,'+'),GenomicSegment('NC_007194.1',4773,4963,'+'),codon_start='1',db_xref=['GI:70989828', 'GeneID:3507996'],locus_tag='AFUA_1G00110',note='encoded by transcript AFUA_1G00110A',old_locus_tag='Afu1g00110',product='hypothetical protein',protein_id='XP_749763.1'),
            SegmentChain(GenomicSegment('NC_007194.1',6804,6881,'-'),GenomicSegment('NC_007194.1',6899,7127,'-'),GenomicSegment('NC_007194.1',7261,7472,'-'),codon_start='1',db_xref=['GI:70989830', 'GeneID:3507997'],locus_tag='AFUA_1G00120',note='encoded by transcript AFUA_1G00120A',old_locus_tag='Afu1g00120',product='hypothetical protein',protein_id='XP_749764.1'),
            SegmentChain(GenomicSegment('NC_007194.1',36278,37475,'-'),codon_start='1',db_xref=['GI:70989846', 'GeneID:3508018'],locus_tag='AFUA_1G00200',note='encoded by transcript AFUA_1G00200A; similar to Ankyrin 1; Erythrocyte ankyrin; Ankyrin R (Swiss-Prot:P16157) [Homo sapiens]',old_locus_tag='Afu1g00200',product='F-box domain and ankyrin repeat protein',protein_id='XP_749772.1'),                           
#                            
#         ]
#         found_chains = [SegmentChain.from_biopython_seqfeature(X,seq.id) for X in features]
#         self.assertEqual(len(expected_chains),len(found_chains),"Not all features read from genbank file! Expected %s, found %s." % (len(expected_chains),len(found_chains)))
#         for expected, found in zip(expected_chains,found_chains):
#             self.assertEqual(expected.get_position_set(),found.get_position_set(),
#                               "Unequal position sets for chain %s. Found %s" % (str(expected),str(found)))
#             found.attr.pop("type")
#             expected.attr.pop("type")
#             self.assertDictEqual(expected.attr,found.attr)
