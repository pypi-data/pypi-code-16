#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='aipfs',

    version='0.0.1',

    description='IPFS daemon asyncio client',

    author='faisalburhanufin',

    author_email='faisalburhanudin@hotmail.net',

    url='https://github.com/faisalburhanudin/aipfs',

    download_url='https://github.com/faisalburhanudin/aipfs/archive/0.0.1.tar.gz',

    install_requires=[
        "aiohttp >= 1.2.0"
    ],

    packages=find_packages(),
)
