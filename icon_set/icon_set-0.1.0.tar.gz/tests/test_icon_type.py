#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct

import pytest

from icon_set.exceptions import InvalidIconTypeError
from icon_set.icon_type import IconType


@pytest.mark.parametrize('os_type', ('', 'I', 'ICONZ'))
def test_raises_if_os_type_is_not_4_bytes(os_type):
    with pytest.raises(InvalidIconTypeError):
        IconType(os_type, size=42)  # We don't care about size here


@pytest.mark.parametrize(
    'size, description',
    [(0, ''), (42, 'Lorem ipsum.')]
)
def test_icon_type_is_always_4_bytes(size, description):
    # When
    icon_type = IconType('ICON', size, description)

    # Then
    assert len(icon_type.as_bytearray()) == 4


@pytest.mark.parametrize('os_type', ['ICN#', 's8mk', 'TOC '])
def test_all_4_bytes_are_os_type(os_type):
    # Given
    os_type_as_bytearray = bytearray(os_type, encoding='ascii')

    # When
    icon_type = IconType(os_type, size=42)  # We don't care about size here

    # Then
    assert icon_type.as_bytearray() == os_type_as_bytearray
