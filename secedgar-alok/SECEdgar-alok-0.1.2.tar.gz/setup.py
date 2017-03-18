# -*- coding:utf-8 -*-
import os
import sys

from setuptools import setup, find_packages
from setuptools import Command
from setuptools.command.install import install
from subprocess import call
from glob import glob
from os.path import splitext, basename, join as pjoin

SUPPORTED_VERSIONS = [
    '3.4',
    '3.5',
    '3.6',
]

setup(
    name='SECEdgar-alok',
    version='0.1.2',
    packages=find_packages(),
    package_dir={'SECEdgar': 'SECEdgar'},
    url='https://github.com/Alok/SEC-Edgar',
    license='Apache License (2.0)',
    author='Alok Singh',
    author_email='alokbeniwal@gmail.com',
    description='SEC-Edgar implements a basic Sphinx crawler for downloading the   \
                 filings. It provides an interface to extract the filing from the SEC.gov site \
                 You might find it most useful for tasks involving automated  \
                 data collection of filings from SEC.gov',
    entry_points='''
            [console_scripts]
            ''',
    cmdclass={
        'install': install,
    },
    install_requires=[
        'requests',
        'beautifulsoup4',
        'configparser',
    ],
    keywords=['SEC', 'Edgar', 'Crawler', 'filings'],
    tests_require=['pytest'],
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
