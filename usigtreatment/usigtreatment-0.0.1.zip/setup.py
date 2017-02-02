# -*- coding: utf-8 -*-

from setuptools import setup,find_packages

import usigtreatment

setup(name='usigtreatment',
version = usigtreatment.__version__,
packages=find_packages(),
author='Krounet',
author_email='krounet@gmail.com',
description="Utility functionnalities for signal treatments",
long_description=open('README.md').read(),
include_package_data=True,
classifiers=["Programming Language :: Python",
"Development Status :: 1 - Planning",
"Natural Language :: French",
"Operating System :: OS Independent",
"Programming Language :: Python :: 2.7",
"Topic :: Scientific/Engineering"],
license="WTFPL")

