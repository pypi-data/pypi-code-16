# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_ = f.read()

setup(
    name='permoize',
    version='0.1.0',
    description='A persistent memoization library for Python',
    long_description=readme,
    author='Ivan Dmitrievsky',
    author_email='ivan.dmitrievsky+python@gmail.com',
    url='https://github.com/idmit/permoize',
    install_requires=[
        'diskcache'
    ],
    license=license_,
    packages=find_packages(exclude=('tests', 'docs'))
)
