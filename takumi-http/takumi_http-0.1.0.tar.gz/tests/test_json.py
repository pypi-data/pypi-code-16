# -*- coding: utf-8 -*-

import pytest
from thriftpy.thrift import TType, TPayload, TDecodeException


class Value(TPayload):
    thrift_spec = {
        1: (11, 'hello', False),
        2: (15, 'world', 11, False),
        5: (8, 'f1', True),
        7: (15, 'f3', (15, 8), True)
    }


class System(object):
    pass


@pytest.mark.parametrize('spec,expected', [
    ((11, 'hello', False), (11, 'hello', None, False)),
    ((15, 'world', 11, False), (15, 'world', 11, False)),
    ((13, 'yes', (11, 11), False), (13, 'yes', (11, 11), False)),
    ((12, 'system', System, False), (12, 'system', System, False)),
    ((8, 'f1', True), (8, 'f1', None, True)),
    ((15, 'f2', 8, True), (15, 'f2', 8, True)),
    ((15, 'f3', (15, 8), True), (15, 'f3', (15, 8), True))
])
def test_parse_spec(spec, expected):
    from takumi_http._json import _parse_spec
    assert _parse_spec(spec) == expected


@pytest.mark.parametrize('spec,expected', [
    (11, (11, None)),
    ((15, 8), (15, 8)),
    (System, (System, None)),
])
def test_parse_type_spec(spec, expected):
    from takumi_http._json import _parse_spec
    assert _parse_spec(spec, True) == expected


@pytest.mark.parametrize('ttype,val,spec,expected', [
    (TType.I32, 45, None, 45),
    (TType.DOUBLE, 4.34, None, 4.34),
    (TType.STRING, 'hello', None, 'hello'),
    (TType.BOOL, True, None, True),
    (TType.LIST, [4, 5, 6], TType.I32, [4, 5, 6]),
    (TType.MAP, {'hello': 4, 'world': 123}, (TType.STRING, TType.I32), {
        'hello': 4, 'world': 123
    })
])
def test_to_json(ttype, val, spec, expected):
    from takumi_http._json import _to_json
    assert _to_json(ttype, val, spec) == expected


def test_struct_to_json():
    from takumi_http._json import struct_to_json
    value = Value()
    value.hello = 'world'
    value.world = ['hello', 'world']
    value.f1 = 45
    value.f3 = [[4]]

    assert struct_to_json(value) == {
        'hello': 'world',
        'world': ['hello', 'world'],
        'f1': 45,
        'f3': [[4]]
    }

    value.f1 = None
    with pytest.raises(TDecodeException) as exc:
        struct_to_json(value)
    assert str(exc.value) == \
        "Field 'f1(5)' of 'Value' needs type 'I32', but the value is `None`"

    value.f1 = 'wrong'
    with pytest.raises(TDecodeException) as exc:
        struct_to_json(value)
    assert str(exc.value) == \
        "Field 'f1(5)' of 'Value' needs type 'I32', but the value is `'wrong'`"


@pytest.mark.parametrize('val,ttype', [
    (4, TType.I16),
    (4.4, TType.DOUBLE),
    ('hell', TType.STRING),
    ([4, 5], TType.LIST),
    ({'hello': 90}, TType.MAP),
])
def test_type(val, ttype):
    from takumi_http._json import _is_type_right
    assert _is_type_right(val, ttype)


@pytest.mark.parametrize('val,ttype', [
    (4, TType.STRING),
    ('hell', TType.DOUBLE),
    ([4, 5], TType.MAP),
    ({'hello': 90}, TType.LIST),
])
def test_wrong_type(val, ttype):
    from takumi_http._json import _is_type_right
    assert not _is_type_right(val, ttype)


@pytest.mark.parametrize('ttype,val,spec,expected', [
    (TType.I32, 45, None, 45),
    (TType.DOUBLE, 5, None, 5.0),
    (TType.STRING, 'hello', None, 'hello'),
    (TType.BOOL, True, None, True),
    (TType.LIST, [45, 23], TType.I32, [45, 23]),
    (TType.MAP, {'hello': 123}, (TType.STRING, TType.I32), {'hello': 123})
])
def test_from_json(ttype, val, spec, expected):
    from takumi_http._json import _from_json
    assert _from_json(ttype, val, spec) == expected


def test_struct_from_json():
    from takumi_http._json import struct_from_json
    data = {
        'hello': 'world',
        'world': ['hello', 'world'],
        'f1': 45,
        'f3': [[4]]
    }
    v = Value()
    struct_from_json(data, v)
    assert v.hello == 'world'
    assert v.world == ['hello', 'world']
    assert v.f1 == 45
    assert v.f3 == [[4]]

    v = Value()
    with pytest.raises(TDecodeException) as e:
        struct_from_json({}, v)
    assert str(e.value) == \
        "Field 'f1(5)' of 'Value' needs type 'I32', but the value is `None`"

    data = {'f1': 45, 'f3': [['hello']]}
    with pytest.raises(TDecodeException) as e:
        struct_from_json(data, Value())
    assert str(e.value) == \
        "Field 'f3(7)' of 'Value' needs type 'LIST<LIST<I32>>', but the value is `[['hello']]`" # noqa
