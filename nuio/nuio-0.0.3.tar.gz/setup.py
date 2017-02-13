#!/usr/bin/python3

from setuptools import setup, find_packages
import sys
from os import path

if(sys.version_info.major != 3 or sys.version_info.minor < 5):
	raise SystemError("nuio requires python3.5.1+")

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
	name = "nuio",
	version = "0.0.3",
	description = "A user I/O handler",
	long_description = long_description,
	url = "https://github.com/daknuett/python3-nuio",
	author = "Daniel Knüttel",
	author_email = "daknuett@gmail.com",
	license = "GPL v3",
	classifiers = ['Development Status :: 4 - Beta',
		'Intended Audience :: Developers',

		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Programming Language :: Python :: 3.5'],
	keywords = "input output user stdio",
	packages = find_packages()
     )

