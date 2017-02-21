#!/usr/bin/env python3

from setuptools import find_packages, setup


with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()

with open('README.rst') as readme:
    long_description = readme.read()


setup(
    name='irp',
    version='0.3.0',
    description='Gets possible airports for city names!',
    long_description=long_description,
    url='https://github.com/aerupt/irp',
    author='Lasse Schuirmann',
    author_email='lasse.schuirmann@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=required,
)
