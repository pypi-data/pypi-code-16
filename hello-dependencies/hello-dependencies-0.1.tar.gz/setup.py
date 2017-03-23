#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Ben Lindsay <benjlindsay@gmail.com>

from distutils.core import setup
setup(
  name = 'hello-dependencies',
  packages = ['hello_dependencies'],
  version = '0.1',
  description = 'An attempt to get pip to install dependencies',
  requires=['pandas'],
  install_requires=['pandas'],
  url = 'https://github.com/benlindsay/',
  author = 'Ben Lindsay',
  author_email = 'benjlindsay@gmail.com',
)
