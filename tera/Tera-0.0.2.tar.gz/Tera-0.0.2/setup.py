#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Tera',
    version='0.0.2',
    description='A framework for provisioning and managing your cloud infrastructure using Terraform.',
    author='Steven Normore',
    author_email='steven@dataup.io',
    url='https://tera.dataup.io/',
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
