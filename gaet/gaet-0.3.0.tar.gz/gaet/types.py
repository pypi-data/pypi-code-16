from typing    import NamedTuple, Union, Dict, Optional
from typing.re import Pattern

Gene = NamedTuple('Gene',
        [('id', str), ('type', str), ('product', str), ('length', int), ('digest', int)])

Metric = Optional[Union[bool, int, float]]

MetricGroup = Dict[str, Metric]

# Named regular expression pulled from gaet/gene_types.yml
GenePattern = NamedTuple('GenePattern', [('name', str), ('re', Pattern)])
