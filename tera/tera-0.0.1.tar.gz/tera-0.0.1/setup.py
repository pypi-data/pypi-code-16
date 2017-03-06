#!/usr/bin/env python

from distutils.core import setup

setup(
    name='tera',
    version='0.0.1',
    description='A framework for provisioning and managing your cloud infrastructure using Terraform.',
    author='Steven Normore',
    author_email='steven@normore.me',
    url='https://s.normore.me/',
    packages=['tera', ],
    scripts=[
        'script/bin/tera',
        'script/bin/tera-up',
        'script/bin/tera-down',
    ],
    install_requires=[
        'autopep8==1.2.4',
        'pytest==3.0.6'
    ]
)
