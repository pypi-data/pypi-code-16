#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import logging
import argparse

from antikythera.cli import main, create_parser

def test_cli_verbose():
    test_parser = create_parser()
    args = test_parser.parse_args(['-v'])
    assert args.loglevel == logging.INFO

def test_cli_veryVerbose():
    test_parser = create_parser()
    args = test_parser.parse_args(['-vv'])
    assert args.loglevel == logging.DEBUG

def test_cli_threadsDefualt():
    test_parser = create_parser()
    args = test_parser.parse_args(['-v'])
    assert args.threads == 1

def test_cli_threadsLow():
    test_parser = create_parser()
    args = test_parser.parse_args(['-t 1'])
    assert args.threads == 1

def test_cli_threadsHigh():
    test_parser = create_parser()
    args = test_parser.parse_args(['-t 1000000000000000'])
    assert args.threads == 1000000000000000

def test_cli_capturePath():
    test_parser = create_parser()
    args = test_parser.parse_args(['-c ../data/mycapturefile.pcap'])
    assert args.pcap == ' ../data/mycapturefile.pcap'

def test_cli_interface():
    test_parser = create_parser()
    args = test_parser.parse_args(['-i eth0'])
    assert args.interface == ' eth0'
