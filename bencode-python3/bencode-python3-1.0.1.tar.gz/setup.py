#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 09-02-2017
# @last_modify: Thu Feb  9 18:03:36 2017
##
########################################


from distutils.core import setup
from setuptools import find_packages

setup(
    name='bencode-python3',
    version='1.0.1',
    author='Amyth Arora',
    author_email='mail@amythsingh.com',
    packages=find_packages(),
    url='https://github.com/amyth/bencode',
    license='GPL3 License',
    description='Python 3 port for the official bencode library',
    long_description='This is the python 3 port for the official bencode '\
	    '(Bitorrent) encoding and decoding library. This project supports '\
	    'both python 2 and python 3.',
    zip_safe=False,
    classifiers=[
	# How mature is this project? Common values are
	#   3 - Alpha
	#   4 - Beta
	#   5 - Production/Stable
	'Development Status :: 5 - Production/Stable',

	# Indicate who your project is intended for
	'Intended Audience :: Developers',

	# Specify the Python versions you support here. In particular, ensure
	# that you indicate whether you support Python 2, Python 3 or both.
	'Programming Language :: Python :: 2.6',
	'Programming Language :: Python :: 2.7',
	'Programming Language :: Python :: 3',
	'Programming Language :: Python :: 3.2',
	'Programming Language :: Python :: 3.3',
	'Programming Language :: Python :: 3.4',
	'Programming Language :: Python :: 3.5',
	'Programming Language :: Python :: 3.6',
    ],
)
