#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

import metrovlc

setup(
    name='metrovlc',
    version=metrovlc.__version__,
    packages=find_packages(),
    author='penicolas',
    author_email='png1981@gmail.com',
    description='CLI MetroValencia',
    long_description="README on github : https://github.com/penicolas/metrovlc",
    install_requires=[
        'beautifulsoup4'
    ],
    url='https://github.com/penicolas/metrovlc',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'metrovlc = metrovlc.metrovlc:main',
        ],
    },
)
