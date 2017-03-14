import os
from argtools import command, argument
from .. import sh
from ..utils import iter_tabs
import numpy as np


def random_rgb():
    return (np.random.random_integers(256),
            np.random.random_integers(256),
            np.random.random_integers(256))


#@command.add_sub
@argument('segdup_tab')
def segdup2trackbed(args):
    """
    * set unique name to pairs (use uid)
    * randomize color by name
    """
    with open(args.segdup_tab) as fp:
        rows = iter_tabs(fp)
        header = with_header(rows)
        for row in rows:
            chrom = row['chrom']
            start = row['chromStart']
            end = row['chromEnd']
            name = row['name']
            score = row['score']
            strand = row['strand']
            other_chrom = row['otherChrom']
            other_start = row['otherStart']
            other_end = row['otherEnd']


def require(file):
    if not os.path.exists(file):
        raise Exception('File does not exist: {0}'.format(file))


@command.add_sub
@argument('region_bed', help='with header')
@argument('fasta', help='reference fasta')
@argument('-db', required=True, help='blast db')
@argument('--col-id', default='name', help='column name of region id')
@argument('-o', '--out-dir', default='refdup_analyze')
@argument('-j', '--njobs', type=int, default=8)
@argument('-f', '--force-rerun', action='store_true')
@argument('-m', '--min-size', type=int, default=500)
def bed_refdup_analyze(args):
    """
    Outputs:
        {outdir}/region.fa
        {outdir}/region.ref.blastn
        {outdir}/region.summary.txt
    """
    out_dir = args.out_dir
    region_bed = '{0}/region.bed'.format(out_dir)
    region_fasta = '{0}/region.fa'.format(out_dir)
    region_blastn = '{0}/region.blastn'.format(out_dir)
    region_summary = '{0}/region.summary.txt'.format(out_dir)

    sh.call(['mkdir', '-p', out_dir])

    # create copy of input bed
    if args.force_rerun or not os.path.exists(region_bed):
        sh.call('cat {0} | awk "NR==1; NR>1 && $3-$2 > {min_size}"'.format(
            args.region_bed, min_size=args.min_size),
            stdout=region_bed)

    # make region fasta
    if args.force_rerun or not os.path.exists(region_fasta):
        require(region_bed)
        require(args.fasta)
        sh.call("""
        bedtools getfasta -name -bed <(csvcut -t -c chrom,start,end,{id} {bed} | csvformat -T | sed 1d) -fi {fasta} -fo {out}
        """.format(id=args.col_id, bed=region_bed, fasta=args.fasta, out=region_fasta))

    # make region blastn
    if args.force_rerun or not os.path.exists(region_blastn):
        require(region_fasta)
        sh.call("""blastn -db {db} -num_threads {njobs} -query {fasta} -evalue 0.1 -outfmt '7 std gaps qlen slen qseq sseq'"""
            .format(db=args.db, fasta=region_fasta, njobs=args.njobs),
            stdout=region_blastn)

