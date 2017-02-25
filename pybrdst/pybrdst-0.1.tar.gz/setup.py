# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='pybrdst',
    packages=find_packages(exclude=['tests']),
    version='0.1',
    description='Brazilian daylight saving time',
    long_description=long_description,
    author='João Carlos Mendes',
    author_email='joaocarlos.tmendes@gmail.com',
    url='https://github.com/joaocarlosmendes/pybrdst',
    download_url='https://github.com/joaocarlosmendes/'
        'pybrdst/releases/tag/v0.1',
    license='MIT',
    keywords=['DST',
              'brazilian',
              'daylight',
              'saving',
              'horário',
              'verão',
              'brasileiro'],
    classifiers=[],
    )
