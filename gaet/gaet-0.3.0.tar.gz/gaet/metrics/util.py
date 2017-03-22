import funcy
from typing     import Callable, Dict, Iterable, List
from gaet.types import Gene, MetricGroup

def calculate_group(
        asm: List[Gene],
        partition_f: Callable[[Iterable[Gene]], Dict[str, List[Gene]]],
        metric_f: Callable[[Iterable[Gene]], MetricGroup]
        ) -> Dict[str, MetricGroup]:
    """
    Given a partitioning function and metric calculation function, first partitions
    the assembly groups, then calculates the metrics for the genes in each group.
    """
    return funcy.walk_values(metric_f, partition_f(asm))

def calculate_group_difference(
        asm: List[Gene],
        ref: List[Gene],
        partition_f: Callable[[Iterable[Gene]], Dict[str, List[Gene]]],
        metric_f: Callable[[Iterable[Gene], Iterable[Gene]], MetricGroup]
        ) -> Dict[str, MetricGroup]:
    """
    Given a partitioning function and metric calculation function, first partitions
    the assembly and reference genes into groups, then calculates the metrics for
    the genes in each corresponding group.
    """
    asm_groups = partition_f(asm)
    ref_groups = partition_f(ref)
    return funcy.merge_with(lambda x: metric_f(x[0], x[1]), asm_groups, ref_groups)
