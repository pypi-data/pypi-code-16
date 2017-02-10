# exdoc_example.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0613

from pexdoc import contract
@contract(number='int|float', frac_length='int,>=0', rjust=bool)
def peng(number, frac_length, rjust=True):
    return str(number)
