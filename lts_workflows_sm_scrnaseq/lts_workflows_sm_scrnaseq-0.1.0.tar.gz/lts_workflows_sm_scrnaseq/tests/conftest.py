#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Author: Per Unneberg
Created: Wed Feb  8 09:26:42 2017

"""
import os
import logging
import pytest
from lts_workflows.pytest import plugin as lts_pytest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOTDIR = os.path.abspath(os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir)))
TESTDIR = os.path.join(ROOTDIR, "tests")
EXAMPLESDIR = os.path.join(TESTDIR, "examples")

ENVIRONMENT_FILES = {'py3': lts_pytest.environment_files(path=ROOTDIR, testdir=TESTDIR, filters = ("environment.yaml",)),
                     'py2': lts_pytest.environment_files(path=ROOTDIR, testdir=TESTDIR, filters = ("environment-27.yaml", ))}


def pytest_namespace():
    d = lts_pytest.namespace(**ENVIRONMENT_FILES)
    d.update({'examplesdir' : EXAMPLESDIR,
              'testdir' : TESTDIR})
    return d

def pytest_addoption(parser):
    group = parser.getgroup("lts_workflows_sm_scrnaseq", "single cell rna sequencing options")
    lts_pytest.addoption(group)

def pytest_report_header(config):
    return lts_pytest.report_header(config)

def pytest_runtest_setup(item):
    lts_pytest.slow_runtest_setup(item)
