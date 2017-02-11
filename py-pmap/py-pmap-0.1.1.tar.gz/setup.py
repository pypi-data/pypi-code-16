# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import exists

setup(
    name='py-pmap',
    version='0.1.1',
    description='Pmap package for Python-Guide.org',
    long_description=open('README.rst').read() if exists('README.rst') else '',
    author='Dotan Nahum',
    author_email='jondotan@gmail.com',
    url='https://github.com/jondot/python-pmap',
    license='MIT',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=["futures"])
