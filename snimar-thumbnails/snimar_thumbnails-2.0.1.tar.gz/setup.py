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


try:
    long_description = file('README.md', 'rb').read()
except IOError, e:
    long_description = ''

print find_packages('src')

setup(
    name='snimar_thumbnails',
    version='2.0.1',
    description='Generate thumbnails for the SNIMar local catalogues',
    long_description=long_description,
    license='MIT',
    author='Pedro Dias',
    author_email='pedro.dias@ipma.pt',
    maintainer='Pedro Dias',
    maintainer_email='pedro.dias@ipma.pt',
    keywords=['snimar', 'thumbnails'],
    url='https://bitbucket.org/ipma/snimar_thumbnails',
    install_requires=[
        'OWSLib==0.10.3',
        'Pillow==3.3.1',
        'requests==2.11.1'
    ],
    package_dir={'':'src'},
    packages=find_packages('src'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ]
)
