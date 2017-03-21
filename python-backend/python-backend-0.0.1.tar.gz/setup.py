# -*- coding: utf-8 -*-


import os

from setuptools import setup, find_packages


setup(
    name='python-backend',
    description='Backend for Python',
    license='BSD',
    packages=find_packages(),
    version='0.0.1',
    author='zwczou',
    author_email='zwczou@gmail.com',
    keywords=['backend'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        "requests"
    ],
    classifiers=[],
)
