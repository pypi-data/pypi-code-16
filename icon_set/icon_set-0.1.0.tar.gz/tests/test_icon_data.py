#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct

import pytest

from icon_set.icon_data import IconData
from icon_set.icon_type import IconType


@pytest.fixture
def arbitrary_icon_type():
    return IconType('ICO ', size=0)  # We don't care about size here


@pytest.mark.parametrize(
    'icon_content, number_of_bytes',
    [('', 8), ('a', 9), ('randomimagedata', 23)]
)
def test_icon_data_has_expected_number_of_bytes(icon_content, number_of_bytes):
    # Given
    icon_type = IconType('ICO ', size=0)
    icon = bytearray(icon_content, encoding='ascii')

    # When
    icon_data = IconData(icon_type, icon)

    # Then
    assert len(icon_data.as_bytearray()) == number_of_bytes


def test_first_4_bytes_of_icon_data_is_os_type(arbitrary_icon_type):
    # Given
    icon = bytearray('randomimagedata', encoding='ascii')
    icon_data = IconData(arbitrary_icon_type, icon)

    # When
    first_4_bytes = icon_data.as_bytearray()[:4]

    # Then
    assert first_4_bytes == arbitrary_icon_type.as_bytearray()


def test_second_4_bytes_of_icon_data_is_length(arbitrary_icon_type):
    # Given
    icon = bytearray('', encoding='ascii')
    icon_data = IconData(arbitrary_icon_type, icon)
    expected_length_packed = struct.pack('>I', 8)

    # When
    second_4_bytes = icon_data.as_bytearray()[4:8]

    # Then
    assert (
        second_4_bytes == bytearray(expected_length_packed)
    )


@pytest.mark.parametrize('icon_content', ['', 'a', 'aaaa'])
def test_8th_byte_onwards_of_icon_data_is_actual_icon_data(
    arbitrary_icon_type,
    icon_content
):
    # Given
    icon = bytearray(icon_content, encoding='ascii')
    icon_data = IconData(arbitrary_icon_type, icon)

    # When
    eighth_byte_onwards = icon_data.as_bytearray()[8:]

    # Then
    assert eighth_byte_onwards == icon
