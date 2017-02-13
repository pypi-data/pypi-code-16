# -*- coding: utf-8 -*-
# =================================================================
#
# Authors: Pedro Dias <pedro.dias@ipma.pt>
#
# Copyright (c) 2016 Pedro Dias
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

from setuptools import setup, find_packages


with open('requirements.txt') as fp:
    INSTALL_REQUIRES = [line for line in fp]

with open('README.txt') as fp:
    LONG_DESCRIPTION = fp.read()


setup(
    name='snimar_pycsw',
    version='2.1.1',
    description='pycsw implementation for the SNIMar project',
    long_description=LONG_DESCRIPTION,
    license='MIT',
    platforms='all',
    author='Pedro Dias',
    author_email='pedro.dias@ipma.pt',
    maintainer='Pedro Dias',
    maintainer_email='pedro.dias@ipma.pt',
    url='https://bitbucket.org/ipma/snimar_pycsw',
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: GIS',
    ]
)
