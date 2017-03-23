#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Ben Lindsay <benjlindsay@gmail.com>

from distutils.core import setup
setup(
  name = 'sim-tree',
  packages = ['sim_tree'], # this must be the same as the name above
  install_requires = ['os', 'pandas', 'time', 'string'],
  version = '0.6',
  description = 'A module for automating hierarchical simulation studies',
  author = 'Ben Lindsay',
  author_email = 'benjlindsay@gmail.com',
  url = 'https://github.com/benlindsay/sim-tree',
  download_url = 'https://github.com/benlindsay/sim-tree/archive/0.6.tar.gz',
  keywords = ['workflow', 'simulations'],
  classifiers = [],
)
