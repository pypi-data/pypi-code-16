#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='dynamat2050',
    version='0.0.3',
    description='A library for accessing data from the Dynamat2050 API',
    keywords='energy consumption data API',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    author='Graeme Stuart',
    author_email='gstuart@dmu.ac.uk',
    url='https://github.com/ggstuart/compost',
    packages=find_packages(),
    install_requires=['requests'],
)
