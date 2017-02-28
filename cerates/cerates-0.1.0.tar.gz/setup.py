# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:

    readme = f.read()

with open('LICENSE') as f:

    license = f.read()

setup(

    name='cerates',

    version='0.1.0',

    description='A foreign exchange rates and currency conversion',

    long_description=readme,

    author='Akshay',

    author_email='akshayjr69@gmail.com',

    url='https://github.com/aksbuzz/cerates',

    license=license,

    packages=find_packages(exclude=('tests', 'docs'))
)