# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""


def pytest_addoption(parser):
    parser.addoption("--device", default=None)
