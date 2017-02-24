#!/usr/bin/env python3

from setuptools import setup

import glob

setup(
    name = 'pytrapi',
    packages = ['pytrapi'],
    version = '0.1.1',
    description = "interface for toontown rewritten's web api",
    author = 'Fabian Peter Hammerle',
    author_email = 'fabian.hammerle@gmail.com',
    url = 'https://git.hammerle.me/fphammerle/pytrapi',
    download_url = 'https://git.hammerle.me/fphammerle/pytrapi/archive/0.1.1.zip',
    keywords = ['game', 'api', 'toontown rewritten', 'ttr'],
    classifiers = [],
    # scripts = glob.glob('scripts/*'),
    install_requires = [],
    tests_require = ['pytest'],
    )
