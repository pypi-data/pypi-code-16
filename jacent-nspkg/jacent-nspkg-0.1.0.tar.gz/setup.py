#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='jacent-nspkg',
    version="0.1.0",
    author = 'Jamie Cressey',
    author_email = 'jamiecressey89@gmail.com',
    url = 'https://github.com/jacentio/python-jacent-nspkg',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: Apache Software License',
    ],
    zip_safe=False,
    packages=find_packages(),
)
