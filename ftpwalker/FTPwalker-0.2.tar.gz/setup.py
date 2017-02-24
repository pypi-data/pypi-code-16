#!/usr/bin/env python

from distutils.core import setup

with open("description.rst") as f:
    long_description = f.read()

setup(name='FTPwalker',
      packages=['FTPwalker'],
      version='0.2',
      description='Optimally traversing extremely large FTP directory trees.',
      author='Bohdan Khomtchouk and Kasra Vand',
      author_email='khomtchoukmed@gmail.com, kasraavand@gmail.com',
      url='https://github.com/Bohdan-Khomtchouk/FTPwalker',
      download_url='https://github.com/Bohdan-Khomtchouk/FTPwalker/tarball/0.1',
      keywords=['FTP', 'traverse', 'directory tree', 'optimized'],
      classifiers=[],
      long_description=long_description)
