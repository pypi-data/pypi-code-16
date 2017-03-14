#! /usr/bin/env python

from setuptools import setup

setup(
    name='sco-engine',
    version='0.1.0',
    description='Library to to run predictive models for experiments that are defined in the Standard Cortical Observer Data Store',
    keywords='neuroscience vision cortex ',
    author='Heiko Mueller',
    author_email='heiko.muller@gmail.com',
    url='https://github.com/heikomuller/sco-engine',
    license='GPLv3',
    packages=['scoengine'],
    package_data={'': ['LICENSE']},
    install_requires=['pika']
)
