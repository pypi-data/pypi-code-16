# -*- coding: utf-8 -*-

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='macrocast',
    version='0.00.01',
    description='A forecasting package for macroeconomic data',
    long_description=readme(),
    author='Amir Sani',
    url='http://www.amirsani.com',
    author_email='reachme@amirsani.com',
    download_url='https://github.com/amirsani/macrocast',
    packages=['macrocast'],
    zip_safe=False
)
