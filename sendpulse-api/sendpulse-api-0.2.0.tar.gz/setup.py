"""File for distribution the lib."""
# coding: utf-8

import os
from setuptools import setup, find_packages


def version():
    """Read version."""
    base_dir = os.path.dirname(__file__)

    with open(os.path.join(base_dir, 'sendpulse_api/version.py')) as ver_file:
        ver = dict()
        exec(ver_file.read(), ver)

        return ver['VERSION']


setup(
    name='sendpulse-api',
    version=version(),
    author='Konstantin Kruglov',
    author_email='kruglovk@gmail.com',
    description='',
    url='https://github.com/k0st1an/sendpulse-api',
    packages=find_packages(),
    install_requires=[
        'requests==2.13.0',
    ],
    license='Apache License Version 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: POSIX :: Linux',
    ],
)
