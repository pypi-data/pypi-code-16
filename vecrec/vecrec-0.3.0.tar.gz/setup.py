#!/usr/bin/env python3
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import re
with open('vecrec/__init__.py') as file:
    version_pattern = re.compile("__version__ = '(.*)'")
    version = version_pattern.search(file.read()).group(1)

with open('README.rst') as file:
    readme = file.read()

setup(
    name='vecrec',
    version=version,
    author='Kale Kundert',
    author_email='kale@thekunderts.net',
    description='2D vector and rectangle classes',
    long_description=readme,
    url='https://github.com/kxgames/vecrec',
    packages=[
        'vecrec',
    ],
    include_package_data=True,
    install_requires=[
    ],
    license='MIT',
    zip_safe=False,
    keywords=[
        'vecrec',
        '2D',
        'vector',
        'rectangle',
        'library',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ],
)
