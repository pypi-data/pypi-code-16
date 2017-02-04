#!/usr/bin/env python
#coding:utf-8
"""
  Author:  LPP --<Lpp1985@hotmail.com>
  Purpose: 
  Created: 2015/1/1
"""
from distutils.core  import setup
from setuptools import find_packages


import codecs
import os
import sys,glob


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()
NAME = "MicroPipe"

DESCRIPTION = " A package for automated microbe bioinfomatics Analysis"

LONG_DESCRIPTION = read("README.txt")
KEYWORDS = "Pipeline Bioinfomatics"
AUTHOR = "Pengpeng Li"
AUTHOR_EMAIL = "409511038@qq.com"
VERSION = "0.0.57"
#Scripts= glob.glob("MicroPipe/Scripts/*.py")
#Scripts.extend( glob.glob("MicroPipe/*.py")  )
setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = [
        
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
    ],
	url="https://github.com/lpp1985/lpp_Script",
    install_requires=[
        "requests",
        "pandas",
        "numpy",
		"pandas",
		"poster",
		"Pillow",
		"sqlobject",
		"sqlalchemy",
		"redis",
		"termcolor",
		"pyWorkFlow",
		
		
        ],    
    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,

    include_package_data=True,
    zip_safe=True,
    #scripts=Scripts
)
 
