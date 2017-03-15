#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import random
import datetime

import pytest

from hamed_advanced import (alphabet, get, deget, cipher, decipher,
                            get_doy, get_code,
                            get_adavanced_request_code,
                            decode_request_code,
                            get_acception_code,
                            validate_acceptation_code)


@pytest.fixture()
def cercle_id():
    return "33"


@pytest.fixture()
def date():
    return datetime.datetime(2017, 2, 1, 15, 22, 0)


@pytest.fixture()
def request_code():
    return "PJJHNGIGH"


@pytest.fixture()
def acceptation_code():
    return "GJIJJ"


def test_alphabet():
    assert len(alphabet) == 36


def test_get():
    assert get(alphabet, 0, 0) == "a"
    assert get(alphabet, 25, 0) == "z"
    assert get(alphabet, 0, 10) == "k"
    assert get(alphabet, 25, 10) == "9"


def test_deget():
    assert deget(alphabet, "a", 0) == 0
    assert deget(alphabet, "z", 0) == 25
    assert deget(alphabet, "a", 10) == 25
    assert deget(alphabet, "z", 10) == 15


def test_cipher():
    assert cipher("hello world", 5) == "mjqqt 1twqi"
    assert cipher("hello world", 20) == "1y558 h8c5x"


def test_decipher():
    assert decipher("bonjour", 4) == "6kjfkqn"


def test_cipher_decipher():
    for value in ("hello", "bonjour", "21", "hello monde"):
        pad = random.randint(0, len(alphabet))
        assert decipher(cipher(value, pad), pad) == value


def test_get_doy():
    assert get_doy(datetime.date(2017, 1, 1)) == "001"
    assert get_doy(datetime.date(1982, 11, 21)) == "325"


def test_get_code(cercle_id, date):
    assert get_code(date, cercle_id) == "33170201"


def test_get_adavanced_request_code(cercle_id, date, request_code):
    assert get_adavanced_request_code(cercle_id, date) == request_code


def test_decode_request_code(cercle_id, date, request_code):
    dcercle_id, ddate, dpad = decode_request_code(request_code)
    assert dcercle_id == cercle_id
    assert ddate == date.date()
    assert dpad == date.hour


def test_get_acception_code(request_code, acceptation_code):
    dacception_code = get_acception_code(request_code)
    assert dacception_code == acceptation_code


def test_validate_acceptation_code(request_code, acceptation_code):
    assert validate_acceptation_code(request_code, acceptation_code)
    assert not validate_acceptation_code(request_code + "A", acceptation_code)
    assert not validate_acceptation_code(request_code, acceptation_code + "A")
