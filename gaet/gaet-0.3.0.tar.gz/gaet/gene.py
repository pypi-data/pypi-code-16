import funcy

from typing     import Iterable, Callable, List, Dict, Tuple, Set
from functools  import reduce
from gaet.types import Gene, GenePattern

import gaet.util as util


def partition_genes_by_product(product_regexes: Set[GenePattern], genes: Iterable[Gene]) -> Dict[str, List[Gene]]:
    """
    Partitions a list of genes into groups based on regular expression matches to
    their product field.
    """
    def match_product(acc: List[Tuple[str, Gene]], g: Gene) -> List[Tuple[str, Gene]]:
        for p in list(product_regexes):
            if p.re.search(g.product):
                acc.append((p.name, g))
        return acc

    # Reduce list of genes into (group, gene) tuples then group into a dictionary
    # by the first field of the tuple.
    groups = dict(funcy.group_values(reduce(match_product, genes, [])))

    # Fill in any entries not found with an empty array
    for p in product_regexes:
        if p.name not in groups:
            groups[p.name] = []
    return groups


def partition_genes_by_type(genes: Iterable[Gene]) -> Dict[str, List[Gene]]:
    """
    Partitions a list of genes into groups based on their type. Returns a group
    named 'all' including all genes, excluding those not in the list of types in
    'gaet/gene_types/yml'.
    """
    whitelist = set(util.get_yaml_resource('gene_types')['gene_types'])
    whitelist.remove('all')
    is_gene_allowed = lambda gene: gene.type in whitelist
    whitelisted_genes = list(filter(is_gene_allowed, genes))
    groups = dict(funcy.group_by(lambda g: g.type, whitelisted_genes))
    groups['all'] = whitelisted_genes

    # Fill in any groups not found
    for group in whitelist:
        if group not in groups:
            groups[group] = []
    return groups
