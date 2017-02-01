# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='weles',
    version='0.4.1',
    description='A little bit more abstract Machine Learning library.',
    long_description=readme,
    author='Paweł Ksieniewicz',
    author_email='pawel.ksieniewicz@pwr.edu.pl',
    url='https://github.com/w4k2/weles',
    package_data={'': ['LICENSE']},
    license=license,
    packages=find_packages(exclude=('docs', 'tests', 'README.md'))
)
