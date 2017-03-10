#!/usr/bin/env python
from setuptools import setup

setup(
    name='skywise-model',
    version='0.0.15',
    package_data={'': ['README.md']},
    packages=['skywisemodel'],
    install_requires=[
        'skywise-rest-client',
        'voluptuous'
    ],

    # metadata for upload to PyPI
    author='Weather Decision Technologies',
    author_email='jstewart@wdtinc.com',
    description='SkyWise Model API Python Client Library',
    url='https://github.com/wdtinc/skywise-model-py',
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    )
)
