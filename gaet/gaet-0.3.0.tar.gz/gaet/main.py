import sys, os.path, funcy

import ruamel.yaml as yaml
import gaet.gff    as gff
import gaet.util   as util
import gaet.gene   as gene

import gaet.metrics.util       as metric_util
import gaet.metrics.size       as size
import gaet.metrics.count      as count
import gaet.metrics.membership as membership
import gaet.metrics.distance   as dist

from typing     import List, Dict, Optional, Tuple, Any
from gaet.types import MetricGroup, Gene
from funcy      import partial, rpartial


def run() -> str:
    args = util.parse_args(sys.argv[1:])

    assembly     = list(gff.parse_gff_into_genes(util.check_gff_file(args['assembly'])))
    gaet_metrics = {'assembly' : simple_metrics(assembly)}

    if ('reference' in args) and args['reference']:
        reference = list(gff.parse_gff_into_genes(util.check_gff_file(args['reference'])))
        gaet_metrics['reference']  = simple_metrics(reference)
        gaet_metrics['comparison'] = comparison_metrics(assembly, reference)

    dst  = util.destination(args)
    with open(dst, "w") as f:
        doc = "---\n" + yaml.dump(gaet_metrics, default_flow_style = False)
        f.write(doc)
    return ""


def simple_metrics(genes: List[Gene]) -> Any:
    patterns   = set(funcy.mapcat(lambda x: x['products'], util.get_gene_patterns()))
    by_product = partial(gene.partition_genes_by_product, patterns)

    f = partial(metric_util.calculate_group, genes)

    return {"gene_type_size"   : f(gene.partition_genes_by_type, size.group_size),
            "gene_copy_size"   : f(by_product, size.group_size),
            "minimum_gene_set" : membership.singleton_metric_group(genes)}


def comparison_metrics(asm: List[Gene], ref: List[Gene]) -> Any:
    patterns   = set(funcy.mapcat(lambda x: x['products'], util.get_gene_patterns()))
    by_product = partial(gene.partition_genes_by_product, patterns)

    f = partial(metric_util.calculate_group_difference, asm, ref)

    return {'gene_type_distance' : f(gene.partition_genes_by_type, dist.distance_metrics),
            'gene_type_size'     : f(gene.partition_genes_by_type, size.group_size_difference),
            'gene_copy_size'     : f(by_product, size.group_size_difference),
            'gene_copy_distance' : f(by_product, dist.distance_metrics),
            'gene_set_agreement' : membership.membership_agreement(
                                        membership.singleton_metric_group(asm),
                                        membership.singleton_metric_group(ref))}
