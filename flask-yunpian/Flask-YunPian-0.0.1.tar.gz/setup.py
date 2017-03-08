# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()


setup(
    name='Flask-YunPian',
    version='0.0.1',
    description='Flask extension for YunPian API',
    long_description=readme,
    author='codeif',
    author_email='me@codeif.com',
    url='https://github.com/codeif/Flask-YunPian',
    license='MIT',
    install_requires=['requests'],
    packages=find_packages(),
)
