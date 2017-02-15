#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='xnrpc',
    version='1.2.2',
    packages = find_packages(),
    # Project uses , so ensure
    install_requires=[
        "gevent>=1.1.2",
        "zerorpc>=0.6.0",
    ],
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # include any *.msg files found in the 'test' package, too:
        'test': ['*.msg'],
    },
    description='simple rpc based on zerorpc and gevent',
    long_description=open("README.rst").read(),
    url='https://github.com/yidao620c/xnrpc',
    author='Xiong Neng',
    author_email='yidao620@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords=['xnrpc', 'gevent', 'zerorpc', 'subprocess'],
)

