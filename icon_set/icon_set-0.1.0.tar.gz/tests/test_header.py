#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct

import pytest

from icon_set.exceptions import FileLengthTooLargeError
from icon_set.header import Header


def test_raises_when_file_length_is_too_large():
    # Given
    lare_file_length = 0xFFFFFFFF + 1

    # When, then
    with pytest.raises(FileLengthTooLargeError):
        Header(lare_file_length)


def test_header_is_always_8_bytes():
    # Given
    expected_header_length = 8  # Bytes

    # When
    header = Header(file_length=42)  # We don't care about file_length here

    # Then
    assert len(header.as_bytearray()) == expected_header_length


def test_first_4_bytes_of_header_is_the_magic_literal():
    # Given
    magic_literal = bytearray('icns', encoding='ascii')

    # When
    header = Header(file_length=0)  # We don't care about file_length here

    # Then
    assert header.as_bytearray()[:4] == magic_literal


@pytest.mark.parametrize(
    'file_length',
    (0, 2, 128, 1048576, 0xFFFFFFFF)
)
def test_second_4_bytes_of_header_is_the_file_length(file_length):
    # Given
    file_length_packed = struct.pack('>I', file_length)
    file_length_as_bytearray = bytearray(file_length_packed)

    # When
    header = Header(file_length)

    # Then
    assert header.as_bytearray()[4:] == file_length_as_bytearray
