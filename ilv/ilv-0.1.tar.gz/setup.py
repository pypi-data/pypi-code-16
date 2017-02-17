#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages


setup(
    name='ilv',
    version='0.1',
    packages=find_packages(),
    url='http://github.com/yuyu2172/ilv',
    description='Interactive log visualizer for neural networks using Bokeh',
    license='MIT',
    author='Yusuke Niitani',
    author_email='yuyuniitani@gmail.com',
    install_requires=open('requirements.txt').readlines(),
)
