from freezedata import freeze_data
import types
from collections import namedtuple

def test_freeze_data_lists_sets_dicts():
    data = [1, [1, {1, 2, 3}], {1: 2, 2: [1, 2]}]
    control_data = (1, (1, frozenset((1, 2, 3))), types.MappingProxyType({1: 2, 2: (1, 2)}))

    assert freeze_data(data) == control_data


def test_freeze_data_namedtuples_simplenamespaces():
    TestNamedTuple = namedtuple('TestNamedTuple', list('abc'))
    data = types.SimpleNamespace(a=1, b=TestNamedTuple(a=1, b=2, c=3))

    control_tuple = namedtuple('SimpleNamespace', list('ab'))
    control_data = control_tuple(a=1, b=TestNamedTuple(a=1, b=2, c=3))

    assert freeze_data(data) == control_data
