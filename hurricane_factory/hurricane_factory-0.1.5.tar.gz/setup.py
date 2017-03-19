# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requires = f.read()

setup(
    name='hurricane_factory',
    description='Manage CloudFormation at Massive Scale',
    version='0.1.5',
    author='Jared Short',
    author_email='jaredlshort@gmail.com',
    url='https://github.com/trek10inc/hurricane-factory',
    install_requires=requires.split('\n'),
    scripts=['bin/hcf'],
    keywords=['aws', 'cloudformation', 'management', 'orchestration'],
    license='MIT',
    packages=find_packages(exclude=('tests', 'docs'))
)
