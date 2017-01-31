from deepdiff import DeepDiff

import listql


def deep_equal(a, b):
    return DeepDiff(a, b) == {}


def test_select():
    records = [{'a': 1, 'b': 1}, {'a': 2, 'b': 2}]
    selected = listql.select(records, ['a'])
    expected = [{'a': 1}, {'a': 2}]
    assert deep_equal(list(selected), expected)


def test_select_as():
    records = [{'a': 1, 'b': 1}, {'a': 2, 'b': 2}]
    select_as = listql.select(records, {'a': 'c'})
    expected = [{'c': 1}, {'c': 2}]
    assert deep_equal(list(select_as), expected)


def test_group_by():
    records = [{'a': 1}, {'a': 2}, {'a': 1}]
    groups = dict(listql.group(records, 'a'))
    expected = {1: [{'a': 1}, {'a': 1}], 2: [{'a': 2}]}
    assert deep_equal(groups, expected)


def test_accumulate():
    stat = listql.accumulate([{'a': 1}, {'a': 2}], ['a'])
    expected = {'a': 3}
    assert deep_equal(dict(stat), expected)


def test_join():
    t1 = [{'a': 1, 'b': 2}]
    t2 = [{'c': 2, 'd': 3}]
    joined = listql.join(t1, t2, ('b', 'c'))
    expected = [{'a': 1, 'b': 2, 'c': 2, 'd': 3}]
    assert deep_equal(list(joined), expected)
