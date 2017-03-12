#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name='origin',
    version='1.0.2',
    description='Python library for the Origin Event Publisher',
    author='Cochise Ruhulessin',
    author_email='cochise.ruhulessin@wizardsofindustry.net',
    url='https://www.wizardsofindustry.net',
    install_requires=[
        'python-qpid-proton>=0.17.0',
        'dsnparse>=0.1.4'
    ],
    packages=find_packages()
)
