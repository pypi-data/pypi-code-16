# -*- coding: utf-8 -*-

from setuptools import setup
from codecs import open
from os import path

current_dir = path.abspath(path.dirname(__file__))
with open(path.join(current_dir, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='entrydir_pypath',
    version='0.1.0.dev3',
    description='Utility to set up sys.path for source-tree imports',
    long_description=long_description,
    author='Björn Samuelsson',
    author_email='bjorn.samuelsson@anoto.com',
    url='https://pypi.python.org/pypi/entrydir-pypath/',
    license='ICS',
    keywords='path import',
    packages=['entrydir_pypath', 'entrydir_pypath_config'],
    entry_points={
        'console_scripts': ['entrydir-pypath-config = entrydir_pypath_config:main']
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)'
    ]
)
