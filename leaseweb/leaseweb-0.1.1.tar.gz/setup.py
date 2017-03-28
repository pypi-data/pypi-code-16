#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='leaseweb',
    version='0.1.1',
    author="Iwan in 't Groen",
    author_email='iwanintgroen@gmail.com',
    description="Python wrapper for the Leaseweb Virtual Servers API",
    packages=['leaseweb'],
    install_requires=['requests'],
    license="MIT",
    zip_safe=True,
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'leaseweb=leaseweb.api:main',
        ]
    },
)
