import gffutils, pyfaidx, hashlib, tempfile

from typing     import Iterable
from gaet.types import Gene

import gaet.util as util

def gff_to_fasta(path: str) -> pyfaidx.Fasta:
    _, tmp_file = tempfile.mkstemp(suffix = '.fasta', prefix = 'gaet_')
    with open(tmp_file, 'w') as fasta:
        with open(path, 'r') as gff:
            seq_flag = False
            for line in gff:
                if seq_flag:
                    fasta.write(line)
                if line.strip() == '##FASTA':
                    seq_flag = True
    return pyfaidx.Fasta(tmp_file)


def create_digest(s):
    return int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16)


def seq_digest(fasta: pyfaidx.Fasta, f: gffutils.Feature) -> int:
    seq = f.sequence(fasta, use_strand = False)
    if f.strand == "-":
        seq = seq.reverse.complement
    return create_digest(seq.seq)


def determine_product(f: gffutils.Feature) -> str:
    attr_keys = f.attributes.keys()
    if f.featuretype == 'repeat_region':
        return f['rpt_family'][0]
    elif 'product' in attr_keys:
        return f['product'][0]
    else:
        return 'hypothetical protein'


def feature_to_gene(fasta: pyfaidx.Fasta, f: gffutils.Feature) -> Gene:
    return Gene(f.id, f.featuretype, determine_product(f), f.stop - f.start + 1, seq_digest(fasta, f))


def parse_gff_into_genes(path: str) -> Iterable[Gene]:
    try:
        gff = gffutils.create_db(path, dbfn=':memory:').all_features()
    except ValueError:
        util.err_exit('gff_parsing_err', path = path)
    fasta = gff_to_fasta(path)
    return map(lambda x: feature_to_gene(fasta, x), gff)
