# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='py-pmap',
    version='0.1.0',
    description='Pmap package for Python-Guide.org',
    long_description=readme,
    author='Dotan Nahum',
    author_email='jondotan@gmail.com',
    url='https://github.com/jondot/python-pmap',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=["futures"])
