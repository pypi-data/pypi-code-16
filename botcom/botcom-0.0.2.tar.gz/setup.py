#!/usr/bin/env python
from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='botcom',
    version='0.0.2',
    description='command bus',
    long_description=readme(),
    author='Boris Ostretsov',
    license='MIT',
    author_email='ostrbor@gmail.com',
    keywords='bot command bus',
    url='https://github.com/ostrbor/botcom',
    packages=['botcom'], )
