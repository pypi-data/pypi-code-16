#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pyFuckery - exc.py
Created on 2/12/17.

Exception definitions
"""


class FuckeryError(Exception):
    """
    Base exception for pyFuckery errors.
    """


class StorageError(FuckeryError):
    """
    Error doing a memory operation.
    """


class AddressError(StorageError):
    """
    Error related to address violations.
    """


class VMError(FuckeryError):
    """
    Error related to the brainfuck VM
    """


class ExitCondition(VMError):
    """
    Error raised during a exit condition.
    """
