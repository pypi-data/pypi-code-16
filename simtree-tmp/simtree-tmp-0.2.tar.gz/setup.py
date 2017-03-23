#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Ben Lindsay <benjlindsay@gmail.com>

from distutils.core import setup
setup(
  name = 'simtree-tmp',
  packages = ['simtree'],
  version = '0.2',
  description = 'A module for automating hierarchical simulation studies',
  long_description="Long Description",
  requires=['pandas'],
  install_requires=['pandas'],
  author = 'Ben Lindsay',
  author_email = 'benjlindsay@gmail.com',
  url = 'https://github.com/benlindsay/simtree',
  keywords = ['workflow', 'simulations'],
  classifiers = [],
)
