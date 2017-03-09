#!/usr/bin/env python
# coding: utf-8
import sys
from setuptools import setup, find_packages


install_requires = [
    'ecdsa>=0.10',
    'six>=1.5.2',
    'websocket-client>=0.14.0',
    'unirest>=1.1.7'
]


setup(
    name="jingtum-sdk",
    description="Python routines for the Jingtum payment network",
    author='Frank Xu',
    author_email='xuqing@jdwtgroup.com ',
    version="0.9.21",
    url="http://git.jingtum.com/Delida/jingtum_sdk_python.git",
    license='BSD',
    packages=find_packages(),
    zip_safe=True,
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: BSD License',
    ],
    include_package_data=True,
    package_data={
        'jingtumsdk':[
             'config.json'],
    }
)
