import funcy, operator

import gaet.util as util

from typing     import Iterable, Tuple, Dict, List
from functools  import partial
from gaet.types import MetricGroup, Gene, GenePattern

def count_gene_products(genes: Iterable[Gene], pattern: GenePattern) -> Tuple[str, int]:
    """
    For a given GenePattern, returns a count of all matching gene products in the
    list of genes.
    """
    product_names = list(map(lambda g: g.product, genes))
    f = funcy.rcompose(
            partial(map, pattern.re.search),
            partial(filter, funcy.identity),
            list,
            len,
            lambda x: (pattern.name, x))
    return f(product_names)


def all_product_counts(genes: Iterable[Gene], patterns: Iterable[GenePattern]) -> Dict[str, int]:
    """
    Given list of Genes, returns a Dict containing the counts of each GenePattern.
    """
    return dict(map(funcy.func_partial(count_gene_products, genes), patterns))


def gene_count_diff(a: MetricGroup, b: MetricGroup) -> MetricGroup:
    return funcy.merge_with(lambda x: operator.sub(*x), a, b)


def gene_count_metrics(genes: Iterable[Gene]) -> Dict[str, MetricGroup]:
    """
    Calculate the counts for each gene group
    """
    f = lambda x: (str(x['group']), all_product_counts(genes, x['products']))
    return dict(map(f, util.get_gene_patterns()))


def gene_group_difference_metrics(asm: List[Gene], ref: List[Gene]) -> Dict[str, MetricGroup]:
    """
    Calculate the difference in gene counts between the reference and the assembly
    """
    asm_counts = gene_count_metrics(asm)
    ref_counts = gene_count_metrics(ref)
    f = funcy.rcompose(
            partial(map, lambda x: gene_count_diff(*x)),
            partial(zip, asm_counts.keys()),
            dict)
    return f(zip(asm_counts.values(), ref_counts.values()))
