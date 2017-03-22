import funcy
from typing          import Iterable, Dict, TypeVar, Callable, Optional, List, Union
from functools       import partial
from gaet.types      import Metric, MetricGroup, Gene
from gaet.functional import identity, ffirst

import gaet.util as util
import gaet.gene as gene

SizeTransform = Callable[[Iterable[int]], Iterable[int]]


def calculate(f: SizeTransform, threshold: Union[int, float], xs: Iterable[int]) -> Optional[int]:
    """
    Calculate size-related metrics. Given a list of integers, select the first value
    where the first value from the running cumulative sum of the ordered list of
    values is greater than the given threshold value.

    Keyword Arguments:

    f         -- a function taking a list of integers and returning a list of
                 integers. Used to transform the integer list when calculating the
                 threshold metric.

    threshold -- integer at which to return the first transformed value for which
                 the running cumulative is greater than this.

    xs        -- list of integers to calculate this metric for
    """
    sorted_xs     = sorted(xs, reverse = True)
    trsfm   = zip(f(sorted_xs), funcy.sums(sorted_xs))
    value = ffirst(funcy.dropwhile(lambda x: x[1] < threshold, trsfm))
    if value:
        return int(value)
    else:
        return None


def nx(xs: Iterable[int], threshold: Union[int, float]) -> Optional[int]:
    """
    Calculate the size metric using the identity transform, e.g. ng50.
    """
    return calculate(lambda x: map(identity, x), threshold, xs)


def lx(xs: Iterable[int], threshold: Union[int, float]) -> Optional[int]:
    """
    Calculate the size metric using the value's index. e.g. lg50.
    """
    increment_index = lambda y: y[0] + 1
    f = lambda x: map(increment_index, enumerate(x))
    return calculate(f, threshold, xs)


def gene_lengths(genes: Iterable[Gene]) -> int:
    return list(map(lambda x: x.length, genes))


def metric_difference(a: MetricGroup, b: MetricGroup) -> MetricGroup:
    """
    Calculate the difference in two metric groups by subtracting the reference
    metrics from the assembly metrics.
    """
    def _f(metrics: List[Metric]) -> Metric:
        if any(map(lambda x: x is None, metrics)):
            return None
        else:
            return metrics[0] - metrics[1]
    return funcy.walk_values(_f, funcy.merge_with(list, a, b))


def group_size(genes: Iterable[Gene]) -> MetricGroup:
    """
    Calculate the set of size metrics for a given list of genes
    """
    sizes = gene_lengths(genes)
    sum_length = sum(sizes)
    half_assembly = sum_length / 2.0
    return {"sum_length" : sum_length,
            "count"      : len(sizes),
            "n50"        : nx(sizes, half_assembly),
            "l50"        : lx(sizes, half_assembly)}


def group_size_difference(asm: Iterable[Gene], ref: Iterable[Gene]) -> MetricGroup:
    """
    Calculate the set of size metrics for a given list of genes, using the length of
    reference genes as the threshold value.
    """
    sizes = gene_lengths(asm)
    half_ref_assembly = sum(gene_lengths(ref)) / 2.0
    reference_metrics = {"ng50" : nx(sizes, half_ref_assembly),
                         "lg50" : lx(sizes, half_ref_assembly)}
    difference_metrics = metric_difference(group_size(asm), group_size(ref))
    return funcy.merge(reference_metrics, difference_metrics)
