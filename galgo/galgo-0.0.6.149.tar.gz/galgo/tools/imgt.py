from __future__ import print_function
from argtools import command, argument
from itertools import dropwhile, chain, groupby
from builtins import filter, zip
from collections import namedtuple, defaultdict
import logging
import re
import os
import time
from .. import sh
from ..utils import cached_property, collect_while, skip_until, isblank, make_not, blank_split
from ..bioseq import dna_revcomp, dna_translate
from ..blast import BlastTabFile
import pandas as pd
import numpy as np
from joblib import Parallel, delayed


class IMGTNucFile:
    '''
    Example:
        <header>

        HLA-A Nucleotide Sequence Alignments
        IMGT/HLA Release: 3.24.0.1
        Sequences Aligned: 2016 May 04
        Steven GE Marsh, Anthony Nolan Research Institute.
        Please see http://hla.alleles.org/terms.html for terms of use.


    '''
    @staticmethod
    def _parse_lines(nuc_file):
        with open(nuc_file) as fp:
            try:
                it = fp
                headers, it = collect_while(make_not(isblank), it)
                bodies = []
                logging.info('Read headers')

                # body
                while 1:
                    data = {}
                    _, it = collect_while(isblank, it)  # skip blank lines

                    line = next(it).rstrip()
                    logging.debug(line)
                    tokens = blank_split(line)
                    if tokens[0] != 'cDNA':
                        raise StopIteration
                    data['dna_poss'] = list(map(int, tokens[1:]))

                    line = next(it).rstrip()
                    logging.debug(line)
                    if line.strip().startswith('AA'):
                        tokens = blank_split(line)
                        assert tokens[0] == 'AA' and tokens[1] == 'codon'
                        data['aa_poss'] = list(map(int, tokens[2:]))
                        line = next(it).rstrip()
                        logging.debug(line)

                    data['offsets'] = [i for i, s in enumerate(line) if s == '|']

                    data['lines'], it = collect_while(make_not(isblank), it)
                    logging.debug('%s', data['lines'][0].rstrip())
                    if len(data['lines']) > 1:
                        logging.debug('%s', data['lines'][1].rstrip())
                    logging.debug('Read %s subtypes', len(data['lines']))
                    bodies.append(data)
            except StopIteration as e:
                pass
            logging.info('Read bodies')
        return headers, bodies

    def __init__(self, nuc_file):
        headers, bodies = self._parse_lines(nuc_file)
        # headers
        self.name = headers[0].rstrip()
        self.gene = self.name.split(' ')[0]  # HLA-A
        self.version = headers[1].rstrip().split(':')[1].strip()  # 3.24.0.1
        # bodies
        self.gene_info = []
        offsets = []
        self.subtypes = subs = [blank_split(line)[0] for line in bodies[0]['lines']]
        sub_alns = dict((subtype, []) for subtype in subs)  # {subtype: [exon alignment]}
        for body in bodies:
            offsets.extend(body['offsets'])

            # the first line of each body block is the refenence alignment
            line = body['lines'][0]
            tokens = blank_split(line)
            subtype = tokens[0]
            ref_aln = ''.join(tokens[1:])
            sub_alns[subtype].append(ref_aln)
            for line in body['lines'][1:]:
                tokens = blank_split(line)
                subtype = tokens[0]
                raw_aln = ''.join(tokens[1:])
                aln = decode_seq(raw_aln, ref_aln)
                sub_alns[subtype].append(aln)

        logging.info('Load %s subtypes', len(subs))
        logging.info('Alignment block length: %s', len(ref_aln))
        self.subtype_nucs = dict((sub, IMGTNuc(sub, ''.join(sub_alns[sub]))) for sub in subs)


def decode_seq(seq, ref, same='-'):
    """
    >>> decode_seq('-G-.-A.-*-', 'ATACTTTG..')
    'AGA.TA.G*.'
    """
    return ''.join(r if a == same else a for a, r in zip(seq, ref))

def get_exon_frames(exon_seqs):
    """
    >>> get_exon_frames(['***GC*', 'GA****'])
    [(0, 0), (0, 0)]
    >>> get_exon_frames(['AT', 'GCTTTA', 'AT'])
    [(0, 2), (2, 2), (2, 1)]
    >>> get_exon_frames(['ATT'])
    [(0, 0)]
    """
    frames = []
    right = 0
    for seq in exon_seqs:
        left = right
        right = (left + len(seq)) % 3
        frames.append((left, right))
    return frames

class IMGTNuc:
    def __init__(self, name, aln):
        """
        name: A*01:01:01:02N
        aln: ATGGCCGTCATGGCGCCCCGAACCCTCCTC...
        """
        raw_sep_seq = aln.replace('.', '')  # remove deletion char
        raw_exon_seqs = raw_sep_seq.split('|')  # exons with '*'
        exon_frames = get_exon_frames(raw_exon_seqs)

        self.seq = raw_sep_seq.replace('|', '')
        self.exons = raw_exon_seqs
        self.exon_frames = exon_frames


@command.add_sub
@argument('nuc')
def imgt_nuc2exon(args):
    parsed = IMGTNucFile(args.nuc)
    print ('subtype', 'number', 'is_typed', 'lphase', 'rphase', 'length', 'seq', sep='\t')
    for subtype in parsed.subtypes:
        nuc = parsed.subtype_nucs[subtype]
        for number, (seq, (lphase, rphase)) in enumerate(zip(nuc.exons, nuc.exon_frames), 1):
            is_typed = int('*' not in seq)
            print (subtype, number, is_typed, lphase, rphase, len(seq), seq, sep='\t')


#@command.add_sub
@argument('gen')
def imgt_gen(args):
    pass


#@command.add_sub
@argument('prot')
def imgt_prot(args):
    pass

@command.add_sub
@argument('contigs')
@argument('-d', '--imgt-dir', default=None)
@argument('-g', '--imgt-gen', default=None)
@argument('-l', '--allele-list', default=None)
@argument('-o', '--out-dir', default='imgt_classify_hla')
@argument('-t', '--target-genes', nargs='+', default=['A', 'B', 'C'])
@argument('-f', '--force-rerun', action='store_true')
@argument('--dry-run', action='store_true')
@argument('--EST2GENOME', default='est2genome')
@argument('-j', '--njobs', type=int, default=8)
def imgt_classify_hla(args):
    """
    Currently, classical imgt type only

    Inputs:
        {imgt_dir}/fasta/{gene}_nuc.fasta
        gen.fasta
        required files under {imgt_aln_dir}
        *_nuc.txt is required for identify the exon number contained in cDNA (*_nuc.fasta)
        *_nuc.txt

    Outputs:
        {outdir}/{gene}_nuc.exons.txt
        {outdir}/{gene}_nuc.fa
        {outdir}/{gene}_nuc.fa
        {outdir}/gen.blastdb
        {outdir}/contig.gen.blastn
        {outdir}/contig.gen.blastn.bests
        {outdir}/contigs/{contig_name}.fa
        {outdir}/contigs/{contig_name}.{gene}.est2genome
        {outdir}/contig_summary1.txt
        {outdir}/contig_summary2.txt

    # gene type
    # 4 digit (protein level)
    # 6 digit (exon level)     <= maybe detection of exon 8 will be failed
    # 6G digit (exon 2 and 3) wmda/hla_nom_G.txt
    # 8 digit (outside) if exists
    # variant on exon
    # variant on intron
    """
    contigs_fasta = args.contigs
    gen_fasta_org = args.imgt_gen
    imgt_dir = args.imgt_dir
    allele_list = args.allele_list
    out_dir = args.out_dir
    sh.dry_run = args.dry_run

    sh.call(['mkdir', '-p', out_dir])
    gen_blastdb = '{dir}/gen.blastdb'.format(dir=out_dir)
    gen_blastdb_nhr = gen_blastdb + '.nhr'

    gen_fasta = '{dir}/gen.fa'.format(dir=out_dir)
    contig_gen_blast = '{dir}/contigs.gen.blastn'.format(dir=out_dir)
    contig_gen_blast_bests = '{dir}/contigs.gen.blastn.bests'.format(dir=out_dir)
    contig_cdna_dir = '{dir}/contigs'.format(dir=out_dir)
    closest_exons = '{dir}/contig.closest_exons.txt'.format(dir=out_dir)
    closest_genomes = '{dir}/contig.closest_genomes.txt'.format(dir=out_dir)
    contig_summary = '{dir}/contig.summary.txt'.format(dir=out_dir)
    contig_nuc_fa_tmpl = '{dir}/contig.summary.{{gene}}_nuc.fa'.format(dir=out_dir)
    contig_gen_fa_tmpl = '{dir}/contig.summary.{{gene}}_gen.fa'.format(dir=out_dir)
    exon_counts = {'A': 8, 'B': 7, 'C': 8, 'H': 8}   # TODO more systematic way

    if imgt_dir is None:
        logging.error('imgt_dir is required for preprocss')
        raise Exception('No data directory')

    if args.force_rerun or not os.path.exists(gen_fasta) or os.path.getsize(gen_fasta) < 1:
        require(gen_fasta_org)
        galgo(r'''fa_select {fasta} -n $(cat {list} | awk '{{print "HLA:" $1}}' | tr '\n' ' ') > {out_fasta}'''
                .format(fasta=gen_fasta_org, list=allele_list, out_fasta=gen_fasta),
                stdout=2)

    if args.force_rerun or not os.path.exists(gen_blastdb_nhr):
        require(gen_fasta)
        sh.call('makeblastdb -in {fasta} -out {db} -dbtype nucl -parse_seqids'.format(fasta=gen_fasta, db=gen_blastdb))
        #sh.call_if('', 'wc -l {fasta}')

    if args.force_rerun or not os.path.exists(contig_gen_blast):
        require(gen_blastdb_nhr)
        sh.call("""blastn -db {db} -num_threads {njobs} -query {fasta} -evalue 0.1 -outfmt '7 std gaps qlen slen qseq sseq'"""
            .format(db=gen_blastdb, fasta=contigs_fasta, njobs=args.njobs),
            stdout=contig_gen_blast)

    #@after(indexing)
    if args.force_rerun or not os.path.exists(contig_gen_blast_bests):
        require(contig_gen_blast)
        require(allele_list)
        if not args.dry_run:
            _create_best_contigs(contig_gen_blast, allele_list, contig_gen_blast_bests)

    for gene in args.target_genes:
        nuc = '{dir}/{gene}_nuc.fa'.format(dir=out_dir, gene=gene)
        if args.force_rerun or not os.path.exists(nuc) or os.path.getsize(nuc) < 1:
            galgo(r'''fa_select {org_fasta} -n $(cat {list} | awk '{{print "HLA:" $1}}' | tr '\n' ' ') > {out_fasta}'''
                    .format(
                        org_fasta='{imgt_dir}/fasta/{gene}_nuc.fasta'.format(imgt_dir=imgt_dir, gene=gene),
                        list=allele_list,
                        out_fasta=nuc))

    #    {outdir}/contigs/{contig_name}.fa
    #    {outdir}/contigs/{contig_name}.{gene}.est2genome
    if not args.dry_run:
        require(contig_gen_blast_bests)
        sh.call('mkdir -p {dir}'.format(dir=contig_cdna_dir))
        env = {'out_dir': out_dir, 'args': args, 'contig_cdna_dir': contig_cdna_dir}   # workaround
        Parallel(n_jobs=args.njobs, backend='threading')(delayed(run_est2genome)(name, gene, env) for name, gene in extract_contig_genes(contig_gen_blast_bests))

    def run_classify_hla():
        require(contig_gen_blast_bests)
        require(allele_list)
        def find_closest_exons(name, gene):
            est2genome_parsed = '{dir}/{name}.{gene}_nuc.est2genome.txt'.format(dir=contig_cdna_dir, name=name, gene=gene)
            require(est2genome_parsed)
            tab = pd.read_table(est2genome_parsed)
            tab = tab[tab.category == 'span'].sort_values('edit_distance').sort_values('number', ascending=False).reset_index()
            #logging.info(tab)
            min_edit = tab['edit_distance'].loc[0]
            logging.info((name, gene, min_edit, tab.edit_distance.min()))
            return tab[tab.edit_distance == min_edit]

        def find_full_matched_exons(name, gene):  # TODO check if full length nuc was matched (maybe you have to read nuc lengths from fasta)
            est2genome_parsed = '{dir}/{name}.{gene}_nuc.est2genome.txt'.format(dir=contig_cdna_dir, name=name, gene=gene)
            require(est2genome_parsed)
            tab = pd.read_table(est2genome_parsed)
            tab = tab[(tab.category == 'span')
                    & (tab.number == exon_counts[gene])
                    & (tab.regular_intron == exon_counts[gene] - 1)].sort_values('edit_distance').reset_index()

            #logging.info(tab)
            min_edit = tab['edit_distance'].loc[0]
            logging.info((name, gene, min_edit, tab.edit_distance.min()))
            tab = tab[tab.edit_distance == min_edit]

            # TODO should check aa before edit distance?
            tab['qseq_aa'] = tab.qseq.map(lambda x: dna_translate(x.replace('|', '').replace('-', '')))  # db seq
            tab['rseq_aa'] = tab.rseq.map(lambda x: dna_translate(x.replace('|', '').replace('-', '')))  # contig seq
            tab['aa_match'] = tab['qseq_aa'] == tab['rseq_aa']
            return tab


        contig_genes = list(extract_contig_genes(contig_gen_blast_bests))

        def get_matched_exons():
            #tab = pd.concat(find_closest_exons(name, gene) for name, gene in contig_genes)
            tab = pd.concat(find_full_matched_exons(name, gene) for name, gene in contig_genes)
            return tab

        def get_top_genomes():
            tab1 = pd.read_table(contig_gen_blast_bests)
            #tab = pd.concat(find_closest_exons(name, gene) for name, gene in extract_contig_genes(contig_gen_blast_bests))
            def gen_tops():
                for sname, tab in tab1.groupby('qname'):
                    tab = tab.sort_values('edit_distance').reset_index()
                    #logging.info(tab)
                    min_edit = tab['edit_distance'].loc[0]
                    #logging.info(min_edit)
                    yield tab[tab.edit_distance == min_edit]

            tab = pd.concat(gen_tops())
            return tab

        def get_consistent_genomes(qname_subtype_6ds):
            tab1 = pd.read_table(contig_gen_blast_bests)
            #tab = pd.concat(find_closest_exons(name, gene) for name, gene in extract_contig_genes(contig_gen_blast_bests))
            tab1['subtype_6d'] = tab1['subtype'].apply(lambda x: ':'.join(x.split(':')[:3]))

            def gen_tops():
                for qname, tab in tab1.groupby('qname'):
                    subtype_6ds = qname_subtype_6ds.get(qname, [])
                    yield pd.concat(
                            tab[tab['subtype_6d'] == s].sort_values(['edit_distance', 'aln_len'], ascending=[True, False]).nsmallest(1, columns=['edit_distance'])
                            for s in subtype_6ds)

            tab = pd.concat(gen_tops())
            return tab

        tab = get_matched_exons()
        alist = _read_allele_list(allele_list)
        tab = tab.merge(alist, left_on='qname', right_on='id')#, rsuffix='.1')
        tab = tab[tab.columns.difference(['qseq', 'rseq'])] #+ tab[['qseq', 'rseq']]
        tab.sort_values('rname', inplace=True)
        tab.to_csv(closest_exons, sep='\t', index=False)
        logging.info('Create %s', closest_exons)

        # summary contig info
        tab1 = tab[['rname', 'qname', 'subtype', 'edit_distance', 'subtype_6d', 'subtype_4d', 'aa_match']]
        #tab1['subtype_6d'] = tab1['subtype'].apply(lambda x: ':'.join(x.split(':')[:3]))
        #tab1.loc[:, 'subtype_6d'] = tab1['subtype'].apply(lambda x: ':'.join(x.split(':')[:3]))
        #tab1.loc[:, 'subtype_4d'] = tab1['subtype'].apply(lambda x: ':'.join(x.split(':')[:2]))

        contig_info = {}
        # gene
        for name, gene in contig_genes:
            contig_info[name] = {}
            contig_info[name]['gene'] = gene

        # exon
        for name, t in tab1.groupby('rname'):
            contig_info[name]['edit_6d'] = ed = list(t.edit_distance)[0]  # only one for edit 6d
            contig_info[name]['closest_6d'] = closest_6d = list(sorted(t.subtype_6d.unique()))
            contig_info[name]['closest_4d'] = closest_4d = list(sorted(t.subtype_4d.unique()))
            contig_info[name]['aa_match'] = aa_match = [list(t[t.subtype_4d == sub].aa_match)[0] for sub in closest_4d]
            if ed == 0: # exact
                contig_info[name]['exact_6d'] = contig_info[name]['closest_6d'][0]
            if len(aa_match) > 0 and np.any(aa_match): # exact
                idx_match = np.argmax(aa_match)
                contig_info[name]['exact_4d'] = closest_4d[idx_match]

        #tab = get_top_genomes()
        #tab.sort_values('qname', inplace=True)
        #tab.to_csv(closest_genomes, sep='\t', index=False)
        #logging.info('Create %s', closest_genomes)
        contig_closests = dict((name, d['closest_6d']) for name, d in contig_info.items())

        tab = get_consistent_genomes(contig_closests)
        tab.sort_values('qname', inplace=True)
        tab.to_csv(closest_genomes, sep='\t', index=False)
        logging.info('Create %s', closest_genomes)

        #tab1 = tab[['qname', 'subtype', 'edit_distance']]
        tab['exact_6d'] = tab1['subtype'].apply(lambda x: ':'.join(x.split(':')[:3]))

        # genomes
        for name, t in tab.groupby('qname'):
            t = t.sort_values(['edit_distance', 'aln_len'], ascending=[True, False])
            contig_info[name]['edit_8d'] = eds = list(t.edit_distance)
            contig_info[name]['closest_8d'] = list(t.subtype)
            contig_info[name]['ref_left_8d'] = list(t.qlclip)  # reference is query here
            contig_info[name]['ref_right_8d'] = list(t.qrclip)
            contig_info[name]['q2s_edit'] = list(t.q2s_edit)  # reference is query here
            contig_info[name]['s2q_edit'] = list(t.s2q_edit)
            if eds and eds[0] == 0: # exact (not only one, but select one with max aln_len)
                contig_info[name]['exact_8d'] = contig_info[name]['closest_8d'][0]

        # list matched imgt types
        for name, info in contig_info.items():
            if len(info.get('closest_8d', [])):  # if closest subtypes exist, restrict to them
                match_digits = [sub.split(':') for sub in info['closest_8d']]
            else:
                match_digits = [sub.split(':') for sub in info['closest_6d']]
            logging.info('match_digits for %s: %s', name, match_digits)
            is_sub = alist.subtype.map(lambda x: any(x.split(':')[:len(d)] == d for d in match_digits))
            contig_info[name]['subs'] = list(alist[is_sub]['subtype'])
            contig_info[name]['subs_id'] = list(alist[is_sub]['id'])


        # finalize
        def iter_contig_info():   # for pandas
            for name, gene in contig_genes:
                d = contig_info[name]
                yield {
                        'refname': name,
                        'gene': gene,
                        'exact_4d': d.get('exact_4d', ''),
                        'exact_6d': d.get('exact_6d', ''),
                        'exact_8d': d.get('exact_8d', ''),
                        'n_closest_4d': len(d.get('closest_4d', [])),
                        'closest_4d': ','.join(d.get('closest_4d', [])),
                        'n_closest_6d': len(d.get('closest_6d', [])),
                        'closest_6d': ','.join(d.get('closest_6d', [])),
                        'edit_6d': d.get('edit_6d', -1),
                        'n_closest_8d': len(d.get('closest_8d', [])),
                        'closest_8d': ','.join(d.get('closest_8d', [])),
                        'ref_right_8d': ';'.join(map(str, d.get('ref_right_8d', []))),
                        'ref_left_8d': ';'.join(map(str, d.get('ref_left_8d', []))),
                        'edit_8d': ';'.join(map(str, d.get('edit_8d', []))),
                        'edit_8d_q2s': ';'.join(map(str, d.get('q2s_edit', []))),
                        'edit_8d_s2q': ';'.join(map(str, d.get('s2q_edit', []))),
                        'subs': ','.join(d.get('subs', [])),
                        'subs_id': ','.join(d.get('subs_id', [])),
                        }

        tab = pd.DataFrame(iter_contig_info(),
                columns='refname gene exact_4d exact_6d exact_8d n_closest_4d closest_4d n_closest_6d closest_6d edit_6d n_closest_8d closest_8d ref_left_8d ref_right_8d edit_8d edit_8d_q2s edit_8d_s2q subs subs_id'.split(' '))
        tab.to_csv(contig_summary, sep='\t', index=False)

    def run_summary_fasta():
        require(contig_summary)
        require(allele_list)
        tab = pd.read_table(contig_summary)
        imgt6d_refnames = {}  # {imgt_6d: first refnames}
        for row in tab[['refname', 'closest_6d', 'subs']].itertuples():
            if not row.closest_6d:
                continue
            names = row.closest_6d.split(',')
            for name in names:
                imgt6d_refnames.setdefault(name, row.refname)

        alist = _read_allele_list(allele_list)
        subtype_hla_ids = defaultdict(lambda : defaultdict(list))   # e.g. {'A': {'A*01:01:01': ['HLA00001', 'HLA02169', 'HLA14798']}}
        hla_id_set = set([sid for subs in tab.subs_id if isinstance(subs, basestring) for sid in subs.split(',')])  # only create fasta from contigs in subs_id
        for row in alist[['id', 'gene', 'subtype_6d']].itertuples():
            if row.id in hla_id_set: #row.subtype_6d in imgt6d_refnames and row.id in hla_id_set:
                subtype_hla_ids[row.gene][row.subtype_6d].append(row.id)

        # create gen file (contig name is like HLA:HLA00001)
        for gene in args.target_genes:
            fasta_ids = ['HLA:' + id for ids in subtype_hla_ids.get(gene, {}).values() for id in ids]
            out_fasta = contig_gen_fa_tmpl.format(gene=gene)
            if not fasta_ids:
                continue
            galgo('fa_select {fasta} -n {names} > {out_fasta}'.format(names=' '.join(fasta_ids), fasta=gen_fasta, out_fasta=out_fasta))

        # create nuc file (contig name is like HLA00001)
        for gene in args.target_genes:
            sh.call(': > {out_fasta}'.format(out_fasta=contig_nuc_fa_tmpl.format(gene=gene)))

        for subtype_6d, refname in imgt6d_refnames.items():
            gene = subtype_6d[0]  # A, B, C, H
            est_fasta = '{dir}/{name}.{gene}_nuc.est2genome.fa'.format(dir=contig_cdna_dir, name=refname, gene=gene)
            out_fasta = contig_nuc_fa_tmpl.format(gene=gene)
            hla_ids = subtype_hla_ids[gene][subtype_6d]
            galgo('fa_select {fasta} -n {hla_ids} >> {out_fasta}'.format(fasta=est_fasta, hla_ids=' '.join(hla_ids), out_fasta=out_fasta))

    if not args.dry_run:
        run_classify_hla()
        run_summary_fasta()


class IMGTHLANamer:
    """
    >>> namer = IMGTHLANamer()
    >>> namer.gen_name('A')
    'A*x1'
    >>> namer.gen_name('A')
    'A*x2'
    >>> namer.gen_name('A', 'A*01')
    'A*01:x1'
    >>> namer.gen_name('B')
    'B*x1'
    """

    def __init__(self):
        self._offsets = defaultdict(int)  # A*01:01 : 1
        self._prefix = 'x'

    def gen_name(self, gene, subtype=None):
        key = (gene, subtype)
        self._offsets[key] += 1
        last = self._prefix + str(self._offsets[key])
        if subtype is None:
            return gene + '*' + last
        else:
            return subtype + ':' + last


def isnan(obj):
    return isinstance(obj, float) and np.isnan(obj)

@command.add_sub
@argument('contig_summary')
def imgt_name(args):
    tab = pd.read_table(args.contig_summary)
    namer = IMGTHLANamer()
    print ('refname', 'imgt_name', sep='\t')
    for row in tab.itertuples():
        gene = row.gene
        subtype = None
        if not isnan(row.exact_4d):
            subtype = row.exact_4d
        if not isnan(row.exact_6d):
            subtype = row.exact_6d
        if not isnan(row.exact_8d):
            subtype = row.exact_8d
        name = namer.gen_name(gene, subtype)
        print (row.refname, name, sep='\t')


@command.add_sub
@argument('allele_list')
@argument('subtype', help='e.g. A*01:01:01')
def imgt_subtypes(args):
    require(args.allele_list)
    alist = _read_allele_list(args.allele_list)
    digits = args.subtype.split(':')
    for row in alist[['id', 'subtype']].itertuples():
        if row.subtype.split(':')[:len(digits)] == digits:  # this is 
            print (row.id, row.subtype, sep='\t')


def galgo(args, **kwds):
    import sys
    if isinstance(args, basestring):
        args = ' '.join((sys.executable, sys.argv[0], args))
    else:
        args = [sys.executable, sys.argv[0]] + list(args)
    return sh.call(args, **kwds)



def run_est2genome(name, gene, env):
    out_dir = env['out_dir']
    contig_cdna_dir = env['contig_cdna_dir']
    args = env['args']
    contigs_fasta = args.contigs
    nuc = '{dir}/{gene}_nuc.fa'.format(dir=out_dir, gene=gene)
    contig = '{dir}/{name}.fa'.format(dir=contig_cdna_dir, name=name)
    est2genome = '{dir}/{name}.{gene}_nuc.est2genome'.format(dir=contig_cdna_dir, name=name, gene=gene)
    est2genome_parsed = '{dir}/{name}.{gene}_nuc.est2genome.txt'.format(dir=contig_cdna_dir, name=name, gene=gene)
    est2genome_fasta = '{dir}/{name}.{gene}_nuc.est2genome.fa'.format(dir=contig_cdna_dir, name=name, gene=gene)
    logging.info('target: %s', est2genome)
    if args.force_rerun or not os.path.exists(est2genome) or os.path.getsize(est2genome) < 1:
        require(contigs_fasta)
        galgo('fa_select {fasta} -n {name} > {contig}'.format(fasta=contigs_fasta, name=name, contig=contig))
        require(contig)
        sh.call('''
        {EST2GENOME} -estsequence {nuc} -genomesequence {contig} -intronpenalty 40 -splicepenalty 1 -mismatch 1 -align 1 -usesplice -outfile {outfile}
        '''.format(EST2GENOME=args.EST2GENOME, nuc=nuc, contig=contig, outfile=est2genome))

    if args.force_rerun or not os.path.exists(est2genome_parsed) or os.path.getsize(est2genome_parsed) < 1:
        require(est2genome)
        galgo('''est2genome_parse {est2genome} > {out}'''.format(est2genome=est2genome, out=est2genome_parsed))

    if args.force_rerun or not os.path.exists(est2genome_fasta) or os.path.getsize(est2genome_fasta) < 1:
        require(est2genome)
        galgo('''est2genome_parse {est2genome} -f fasta > {out}'''.format(est2genome=est2genome, out=est2genome_fasta))

def extract_contig_genes(blast_bests):
    tab = pd.read_table(blast_bests)
    print (tab[tab['rank'] == 0])
    for row in tab[tab['rank'] == 0][['qname', 'gene']].itertuples():
        yield row.qname, row.gene


def _read_allele_list(allele_list, fasta_prefix='HLA:'):
    alist = pd.read_table(allele_list, sep=' ', names=['id', 'subtype'])
    alist['fasta_id'] = fasta_prefix + alist['id']
    alist['gene'] = alist.subtype.map(lambda x: x.split('*')[0])
    alist['subtype_8d'] = alist.subtype.map(lambda x: ':'.join(x.split(':')[:4]))
    alist['subtype_6d'] = alist.subtype.map(lambda x: ':'.join(x.split(':')[:3]))
    alist['subtype_4d'] = alist.subtype.map(lambda x: ':'.join(x.split(':')[:2]))
    alist['subtype_2d'] = alist.subtype.map(lambda x: ':'.join(x.split(':')[:1]))
    return alist

def _create_best_contigs(blastn, allele_list, bests):
    keys = 'qname rank sname gene subtype aln_len qlen slen identity edit_distance mismatches gaps slclip srclip qlclip qrclip left_overhang right_overhang s2q_edit q2s_edit'.split(' ')
    tab = _get_best_contigs(blastn)
    alist = _read_allele_list(allele_list)
    tab = tab.merge(alist, left_on='sname', right_on='fasta_id')#, rsuffix='.1')
    sseq = np.where(tab.is_reverse, tab.sseq.apply(dna_revcomp), tab.sseq)
    sstart = np.where(tab.is_reverse, tab.send, tab.sstart)
    def encode_edit(edit_info):
        return ','.join(('{0}:{1}>{2}'.format(*e) for e in edit_info))
    tab = tab[keys]
    tab.loc[:, 's2q_edit'] = [encode_edit(calc_edit_info(q, s, start)) for q, s, start in zip(tab.qseq, sseq, sstart)]
    tab.loc[:, 'q2s_edit'] = [encode_edit(calc_edit_info(s, q, start)) for s, q, start in zip(sseq, tab.qseq, tab.qstart)]

    #tab.to_csv('/dev/stdout', sep='\t', index=False)
    tab.to_csv(bests, sep='\t', index=False)


def _get_best_contigs(blastn):
    min_sratio = .95
    max_overhang = 20
    #max_edit_distance = 20
    max_edit_distance = 50

    require(blastn)

    with open(blastn) as reader: #, open(summary, 'w+') as writer:
        blast = BlastTabFile(reader)
        def iter_tabs():
            for query, tab in blast.iter_query_tables():
                match_cond = ((tab.sratio >= min_sratio)
                    & (tab.left_overhang <= max_overhang)
                    & (tab.right_overhang <= max_overhang)
                    & (tab.edit_distance <= max_edit_distance))
                tab = tab[match_cond]
                tab = tab.sort_values(['edit_distance', 'aln_len'], ascending=[True, False])
                tab.reset_index(drop=True, inplace=True)
                tab.loc[:, 'rank'] = tab.index
                yield tab

        return pd.concat(iter_tabs()) #ignore_index=True)


def calc_edit_info(query_aln, ref_aln, ref_start=1): #TODO simplify
    """
    #        123 4567   890123456 789012 # offset
    >>> q = 'ACGTCGTTTGG--GACC-GTTTATTCA'
    >>> r = 'AAG-CGTT---ATGTCCAGT-TGTTAA'
    >>> l = list(calc_edit_info(q, r, 3001))
    >>> l[0]
    (3002, 'A', 'C')
    >>> l[1]
    (3004, '', 'T')
    >>> l[2]
    (3008, 'AT', 'TGG')
    >>> l[3]
    (3011, 'T', 'A')
    >>> l[4]
    (3014, 'A', '')
    >>> l[5]
    (3017, '', 'T')
    >>> l[6]
    (3018, 'G', 'A')
    >>> l[7]
    (3021, 'A', 'C')
    """
    assert len(query_aln) == len(ref_aln)
    edits = []
    offset = 0
    apos = ref_start
    for r, q in zip(ref_aln, query_aln):
        if r != q:
            edits.append((apos, offset, r.replace('-', ''), q.replace('-', '')))
        if r == '-':
            offset += 1
        apos += 1

    prev = -float('inf')
    outs = []
    for apos, offset, r, q in edits:
        if apos - prev == 1:
            outs[-1]['ref'] += r
            outs[-1]['query'] += q
        else:
            outs.append({'pos': apos - offset, 'ref': r, 'query': q})
        prev = apos

    return [(out['pos'], out['ref'], out['query']) for out in outs]


def require(file):
    if not os.path.exists(file):
        raise Exception('File does not exist: {0}'.format(file))


@command.add_sub
@argument('est2genome')
@argument('-f', '--format', choices=['tab', 'fasta'], default='tab', help='output format')
def est2genome_parse(args):
    """
    span
        alignment bases
        '|': intron
        # TODO check intron category (regular or irregular)
    """
    with open(args.est2genome) as fp:
        aln_keys = ['edit_distance', 'mismatches', 'gaps', 'qseq', 'rseq']
        if args.format == 'tab':
            print (*('qname qstart qend category number rname rstart rend score match_rate regular_intron'.split(' ') + aln_keys), sep='\t')
            for rec in Est2GenomeRecord.parse(fp):
                aln = [getattr(rec.span, k) for k in aln_keys]
                regular_intron = len([i for i in rec.introns if i.type in '+-'])
                print (rec.qname, rec.span.qstart, rec.span.qend, 'span', len(rec.exons), rec.span.rname, rec.span.rstart, rec.span.rend, rec.span.score, rec.span.match_rate, regular_intron, *aln, sep='\t')
                for num, rec in enumerate(rec.exons, 1):
                    aln = [getattr(rec, k) for k in aln_keys]
                    print (rec.qname, rec.qstart, rec.qend, 'exon', num, rec.rname, rec.rstart, rec.rend, rec.score, rec.match_rate, 0, *aln, sep='\t')
        elif args.format == 'fasta':
            for rec in Est2GenomeRecord.parse(fp):
                print ('>' + rec.qname)
                seqs = []
                last_rend = None
                for num, rec in enumerate(rec.exons, 1):
                    if last_rend is not None:
                        fill_len = rec.rstart - last_rend
                        seqs.append('N' * fill_len)
                    seqs.append(rec.qseq)
                    last_rend = rec.rend
                print (''.join(seqs))



class Est2GenomeRecord:
    #Span = namedtuple('Span', 'score match_rate rstart rend rname qstart qend qname rseq qseq')
    #Exon = namedtuple('Exon', 'score match_rate rstart rend rname qstart qend qname rseq qseq')
    class Feature(namedtuple('Feature', 'score match_rate rstart rend rname qstart qend qname rseq qseq')):
        def __init__(self, *args, **kwds):
            super(Est2GenomeRecord.Feature, self).__init__(*args, **kwds)
            self.mismatches = self.gaps = self.edit_distance = None
            if self.rseq is not None:
                self.mismatches = self.gaps = 0
                for r, q in zip(self.rseq, self.qseq):
                    if r == '|':
                        continue
                    elif r == '-' or q == '-':
                        self.gaps += 1
                    elif r != q:
                        self.mismatches += 1
                self.edit_distance = self.mismatches + self.gaps

    Intron = namedtuple('Intron', 'type score match_rate rstart rend rname')

    """
    """

    _intron_pat = re.compile(r'[\.a-z]+')   # split at 'CGAGGCCGgtgag.....gccagGGTCTCACACTTGGCAGACGATGTATG'

    @staticmethod
    def _is_alignment_start(line):
        tokens = blank_split(line)
        return len(tokens) == 3 and tokens[1] == 'vs' and tokens[2][-1] == ':'

    @staticmethod
    def _is_new_block(line):
        return line.startswith('Note')

    @classmethod
    def parse(cls, fp):
        try:
            it = fp
            #it = dropwhile(lambda x: not _is_new_block(x), it)  # find a line starts with 'Note'
            line, it = skip_until(cls._is_new_block, it)  # find new block
            # body
            while 1:
                splice_lines, it = collect_while(make_not(isblank), it)  # collect exon, intron records
                next(it)  # blank
                span_line = next(it)  # blank
                next(it)  # blank
                segment_lines, it = collect_while(make_not(isblank), it)

                splicings = [blank_split(line.rstrip()) for line in splice_lines]
                segments = [blank_split(line.rstrip()) for line in segment_lines]
                span_row = blank_split(span_line)

                rname = span_row[5]
                qname = span_row[8]
                logging.debug('%s vs %s', rname, qname)

                # find alignment or next block
                line, it = skip_until(lambda x: cls._is_alignment_start(x) or cls._is_new_block(x), it)
                rseqs = qseqs = None
                if cls._is_alignment_start(line):
                    next(it)  # skip blank line
                    rbuf = []
                    qbuf = []
                    while 1:  # reading alignment
                        tokens = blank_split(next(it))  # ref line
                        if not tokens or tokens[0] != rname:  # end of alignment block
                            break
                        rbuf.append(tokens[2])
                        next(it)  # match line
                        tokens = blank_split(next(it))  # query line
                        qbuf.append(tokens[2])
                        next(it)  # blank line

                    rseqs = cls._intron_pat.split(''.join(rbuf))
                    qseqs = cls._intron_pat.split(''.join(qbuf))

                yield cls(span_row, splicings, segments, rseqs, qseqs)
                skip_until(cls._is_new_block, it)
        except StopIteration as e:
            pass

    def __init__(self, span_row, splice_rows, segment_rows, rseqs, qseqs):
        row = span_row
        if rseqs is not None:
            rseq = '|'.join(rseqs)
            qseq = '|'.join(qseqs)
        else:
            rseq = qseq = None
        self.span = self.Feature(int(row[1]), float(row[2]), int(row[3])-1, int(row[4]), row[5], int(row[6])-1, int(row[7]), row[8], rseq, qseq)
        self.exons = []
        self.introns = []
        exon_i = 0
        for row in splice_rows:
            if row[0] == 'Exon':
                if rseqs is not None:
                    rseq = rseqs[exon_i]
                    qseq = qseqs[exon_i]
                else:
                    rseq = qseq = None
                rec = self.Feature(int(row[1]), float(row[2]), int(row[3])-1, int(row[4]), row[5], int(row[6])-1, int(row[7]), row[8], rseq, qseq)
                self.exons.append(rec)
                exon_i += 1
            elif row[0][1:] == 'Intron':
                intron_type = row[0][0] # (+, -, ?)
                rec = self.Intron(intron_type, int(row[1]), float(row[2]), int(row[3])-1, int(row[4]), row[5])
                self.introns.append(rec)
            else:
                logging.error(row)
                raise NotImplementedError

        self.qname = self.span.qname
        self.rname = self.span.rname
        #self.segment_rows = segment_rows  # TODO



def read_vbseq(result, mean_rlen):
    """
    ID      LENGTH  Z       FPKM    THETA
    HLA:HLA00001    1047    0.00    0.0     0.000000e+00
    HLA:HLA00002    1047    0.00    0.0     0.000000e+00
    HLA:HLA00398    1047    0.00    0.0     0.000000e+00
    HLA:HLA00644    1047    0.00    0.0     0.000000e+00
    HLA:HLA00003    1047    45.74   7877.1781230    1.456456e-06
    """
    tab = pd.read_table(result)
    tab['mean_depth'] = 1. * mean_rlen * tab['Z'] / tab['LENGTH']
    return tab


@command.add_sub
@argument('vbseq')
@argument('-a', '--allele-list', required=True, help='IMGT HLA Allelelist')
@argument('--fasta-prefix', default='HLA:', help='HLA prefix of Allelelist')
@argument('-r', '--mean-rlen', required=True, type=float, help='mean read length (if using paired-end mode, set twice of the single read length)')
@argument('--min-depth', type=float, default=0, help='min read depth (only used for output)')
@argument('--min-ratio', type=float, default=0, help='min read ratio (only used for output)')
@argument('--min-het-ratio', type=float, default=.25)
@argument('--min-hom-ratio', type=float, default=.75)
@argument('--hom-x', type=float, default=2.5)
@argument('-g', '--genes', nargs='+')
@argument('-c', '--copy-numbers', nargs='+', type=int)
@argument('-f', '--format', choices=['v0', 'v1'], default='v1', help='version of output format')
@argument('-s', '--sampleid')
def vbseq_hla_gt(args):
    """
    """
    require(args.allele_list)
    logging.info('a prefix of refname is: %s', args.fasta_prefix)
    alist = _read_allele_list(args.allele_list, fasta_prefix=args.fasta_prefix)
    default_cn = 2
    gene_cns = {}
    if args.copy_numbers:
        assert len(args.genes) == len(args.copy_numbers)
        gene_cns = dict(zip(args.genes, args.copy_numbers))

    tab = read_vbseq(args.vbseq, args.mean_rlen)
    tab = tab.merge(alist, left_on='ID', right_on='fasta_id')#, rsuffix='.1')
    if args.genes:
        gene_set = set(args.genes)
        tab = tab[tab.gene.map(lambda x: x in gene_set)]

    del tab['fasta_id']
    del tab['id']
    gene_depths = {}
    for gene, gtab in tab.groupby('gene'):
        gene_depths[gene] = gtab.mean_depth.sum()

    keys = '8d 6d 4d 2d'.split(' ')
    depths = {key: {} for key in keys}
    for key in keys:
        for gkey, gtab in tab.groupby('subtype_' + key):
            depths[key][gkey] = gtab.mean_depth.sum()

    tab['gene_cn'] = tab.gene.map(lambda x: gene_cns.get(x, default_cn))
    tab['gene_depth'] = tab.gene.map(lambda x: gene_depths[x])
    tab['ratio_in_gene'] = tab.mean_depth / tab.gene_depth
    for key in keys:
        d = tab['subtype_' + key].map(lambda x: depths[key][x])
        tab['ratio_' + key] = d / tab.gene_depth

    # add genotype
    def add_gt(tab, id_key='ID', ratio_key='ratio_in_gene', gt_key='gt', sel_key='sel'):
        def get_2copy(gtab):
            gtab = gtab.drop_duplicates(id_key, keep='first')
            tops = gtab[gtab[ratio_key] >= args.min_het_ratio].sort_values(ratio_key, ascending=False)[:2]
            if len(tops) >= 2:
                if tops.iloc[0][ratio_key] >= args.min_hom_ratio:
                    if tops.iloc[0][ratio_key] > tops.iloc[1][ratio_key] * args.hom_x:
                        return ('hom', [tops.iloc[0][id_key]])
                    else:
                        return ('het', [tops.iloc[0][id_key], tops.iloc[1][id_key]])
                else:
                    return ('het', [tops.iloc[0][id_key], tops.iloc[1][id_key]])
            elif len(tops) == 1:
                if tops.iloc[0][ratio_key] >= args.min_hom_ratio:
                    return ('hom', [tops.iloc[0][id_key]])
                else:
                    return ('het', [tops.iloc[0][id_key]])
            else:
                return ('unknown', [])

        def get_1copy(gtab):
            gtab = gtab.drop_duplicates(id_key, keep='first')
            tops = gtab[gtab[ratio_key] >= args.min_hom_ratio].sort_values(ratio_key, ascending=False)[:2]
            if len(tops) >= 1:
                return ('hom', [tops.iloc[0][id_key]])
            else:
                return ('unknown', [])

        gene_gts = {}
        selected_ids = set()
        for gene, gtab in tab.groupby('gene'):
            cn = gtab.iloc[0]['gene_cn']
            if cn == 2:
                gt, ids = get_2copy(gtab)
            elif cn == 1:
                gt, ids = get_1copy(gtab)
            elif cn == 0:
                gt, ids = 'hom', []
            else:
                raise NotImplemented
            gene_gts[gene] = gt
            selected_ids.update(set(ids))

        tab[gt_key] = tab.gene.map(lambda x: gene_gts[x])
        tab[sel_key] = tab[id_key].map(lambda x: int(x in selected_ids))

    add_gt(tab)
    for key in keys:
        add_gt(tab, id_key='subtype_' + key, ratio_key='ratio_' + key, gt_key='gt_' + key, sel_key='sel_' + key)

    #print (tab)
    cond_show = (tab['ratio_in_gene'] >= args.min_ratio) & (tab['mean_depth'] >= args.min_depth)
    tab = tab[cond_show]
    tab = tab.sort_values('gene')
    if args.format == 'v0':
        pass
    if args.format == 'v1':
        tab = convert_hla_gt_format(tab, sampleid=args.sampleid)
    tab.to_csv('/dev/stdout', index=False, sep='\t')


def convert_hla_gt_format(org_tab, sampleid='sampleid'):
    """ # TODO
    emit untyped record?
    emit copy number 0 record?
    """
    digit = 0
    tabs = []
    cols = 'sampleid gene digit subtype gene_cn allele_cn allele sel gene_depth ratio refnames'.split(' ')
    digits = [2, 4, 6, 8, 0]

    for gene, tab1 in org_tab.groupby('gene'):
        for digit in digits:
            if digit == 0:
                id_key = 'ID'
                ratio_key = 'ratio_in_gene'
                gt_key = 'gt'
                sel_key = 'sel'
            else:
                id_key = 'subtype_{0}d'.format(digit)
                ratio_key = 'ratio_{0}d'.format(digit)
                gt_key = 'gt_{0}d'.format(digit)
                sel_key = 'sel_{0}d'.format(digit)

            rtab = tab1.groupby(id_key).agg({'ID': lambda x: ','.join(x)}).rename(columns={'ID': 'refnames'}).reset_index()
            tab2 = tab1.drop_duplicates(id_key, keep='first')
            tab2 = tab2.merge(rtab)
            tab2 = tab2.sort_values(ratio_key, ascending=False).reset_index()
            recs = {col: [] for col in cols}
            for an, rec in enumerate(tab2.itertuples(), 1):
                recs['sampleid'].append(sampleid)
                recs['gene'].append(gene)
                recs['digit'].append(digit)
                recs['gene_cn'].append(rec.gene_cn)
                recs['gene_depth'].append(rec.gene_depth)
                recs['allele'].append(an)
                gt = getattr(rec, gt_key)
                if rec.gene_cn == 0:
                    acn = 0
                elif rec.gene_cn == 1 and gt == 'hom':
                    acn = 1
                elif rec.gene_cn == 2 and gt == 'hom':
                    acn = 2
                elif rec.gene_cn == 2 and gt == 'het':
                    acn = 1
                else:
                    acn = 0
                sel = getattr(rec, sel_key)

                recs['allele_cn'].append(acn * sel)
                recs['subtype'].append(getattr(rec, id_key))
                recs['sel'].append(sel)
                recs['ratio'].append(getattr(rec, ratio_key))
                recs['refnames'].append(rec.refnames)
            tab_out = pd.DataFrame(recs, columns=cols)
            tabs.append(tab_out)

    tab = pd.concat(tabs)[cols]
    return tab


@command.add_sub
@argument('hla_gt_table')
@argument('-s', '--sampleid')
@argument('--min-depth', type=float, default=0, help='min read depth (only used for output)')
@argument('--min-ratio', type=float, default=0, help='min read ratio (only used for output)')
def convert_hla_gt(args):
    """ Update format
    """
    tab = pd.read_table(args.hla_gt_table)
    tab = convert_hla_gt_format(tab, sampleid=args.sampleid)
    cond_show = (tab['ratio_in_gene'] >= args.min_ratio) & (tab['mean_depth'] >= args.min_depth)
    tab = tab[cond_show]
    tab.to_csv('/dev/stdout', index=False, sep='\t')
