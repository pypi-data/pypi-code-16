import funcy, operator

import gaet.util          as util
import gaet.metrics.count as count

from typing     import Iterable
from gaet.types import Gene, MetricGroup, GenePattern


def is_membership_satisfied(genes: Iterable[Gene], products: Iterable[GenePattern]) -> bool:
    counts = count.all_product_counts(genes, products).values()
    return all(map(lambda x: x > 0, counts))

def membership_agreement(a: MetricGroup, b: MetricGroup) -> MetricGroup:
    return funcy.merge_with(lambda x: operator.eq(*x), a, b)

def singleton_metric_group(genes: Iterable[Gene]) -> MetricGroup:
    """
    Calculate group membership metrics for the gene group
    """
    f = lambda x: (str(x['group']), is_membership_satisfied(genes, x['products']))
    return dict(map(f, util.get_gene_patterns()))
