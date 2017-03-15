#!/usr/bin/env python
"""BitlyOauth2ProxySession setup
"""
import os
import codecs
import setuptools


PACKAGENAME = 'bitly-oauth2-proxy-session'
DESCRIPTION = 'LSST Data Management SQuaRE Bitly-Proxy Authenticated Sessions'
AUTHOR = 'Adam Thornton'
AUTHOR_EMAIL = 'athornton@lsst.org'
URL = 'https://github.com/lsst-sqre/BitlyOAuth2ProxySession/'
VERSION = '0.1.5'
LICENSE = 'MIT'


def read(filename):
    '''Convenience function to do, basically, an include'''
    full_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        filename)
    return codecs.open(full_filename, 'r', 'utf-8').read()

LONG_DESCRIPTION = read('README.md')

setuptools.setup(
    name=PACKAGENAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='lsst',
    packages=setuptools.find_packages(exclude=['docs', 'tests*']),
    install_requires=[
        'requests>=2.13.0,<3.0.0',
    ],
)
