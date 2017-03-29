#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Ben Lindsay <benjlindsay@gmail.com>

from distutils.core import setup

desc = 'A module for automating flat or hierarchical job creation and submission'

with open('README.rst', 'r') as f:
    long_desc = f.read()

setup(
  name = 'job_tree',
  packages = ['job_tree'],
  version = '0.4.2',
  description = desc,
  long_description = long_desc,
  requires = ['pandas'],
  install_requires = ['pandas'],
  scripts = ['bin/job_tree'],
  author = 'Ben Lindsay',
  author_email = 'benjlindsay@gmail.com',
  url = 'https://github.com/benlindsay/job_tree',
  keywords = ['workflow', 'simulations'],
  classifiers = [],
)
