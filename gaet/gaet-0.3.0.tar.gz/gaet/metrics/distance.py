import funcy

from collections import defaultdict
from math        import sqrt
from typing      import Any, Iterable, Optional, Set, List, Union
from gaet.types  import Gene, MetricGroup

import gaet.util as util
import gaet.gene as gene


def gene_digest_set(genes: Iterable[Gene]) -> Set[int]:
    return set(map(lambda x: x.digest, genes))

def intersect(a: Iterable[Gene], b: Iterable[Gene]) -> int:
    return len(gene_digest_set(a) & gene_digest_set(b))

def difference(a: Iterable[Gene], b: Iterable[Gene]) -> int:
    return len(gene_digest_set(a) - gene_digest_set(b))

def symmetric_difference(a: Iterable[Gene], b: Iterable[Gene]) -> int:
    return len(gene_digest_set(a) ^ gene_digest_set(b))

def divide(x: int, y: int) -> Optional[float]:
    if y == 0:
        return None
    else:
        return x / float(y)

def norm(a: Iterable[Gene], b: Iterable[Gene], p) -> Union[int, float]:
    counts = defaultdict(lambda: 0)

    for gene in a:
        counts[gene.digest] += 1

    for gene in b:
        counts[gene.digest] -= 1

    if p == 1:
        return sum(map(abs, counts.values()))
    else:
        sqr = lambda x: x**2
        return round(sqrt(sum(map(sqr, counts.values()))), 3)


def distance_metrics(assembly: Iterable[Gene], reference: Iterable[Gene]) -> MetricGroup:
    n_intersect = intersect(assembly, reference)
    n_sym_diff  = symmetric_difference(assembly, reference)
    n_asm       = difference(assembly, reference)
    n_ref       = difference(reference, assembly)
    total       = n_intersect + n_sym_diff

    return {'n_intersect'               : n_intersect,
            'n_assembly_only'           : n_asm,
            'n_reference_only'          : n_ref,
            'n_symmetric_difference'    : n_sym_diff,
            'perc_intersect'            : divide(n_intersect, total),
            'perc_assembly_only'        : divide(n_asm, total),
            'perc_reference_only'       : divide(n_ref, total),
            'perc_symmetric_difference' : divide(n_sym_diff, total),
            'l1_norm'                   : norm(assembly, reference, 1),
            'l2_norm'                   : norm(assembly, reference, 2)}
