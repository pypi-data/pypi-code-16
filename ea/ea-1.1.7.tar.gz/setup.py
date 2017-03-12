#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name='ea',
    version='1.1.7',
    description='Enterprise Architecture Library',
    author='Cochise Ruhulessin',
    author_email='cochiseruhulessin@gmail.com',
    url='https://www.wizardsofindustry.net',
    install_requires=[
        'six',
        'marshmallow',
        'phonenumbers',
        'dsnparse',
        'pytz',
        'jinja2'
    ],
    packages=find_packages()
)
