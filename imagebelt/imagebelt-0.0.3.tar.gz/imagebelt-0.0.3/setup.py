#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# notez qu'on import la lib
import imagebelt.imagebelt

#
setup(
    #
    name='imagebelt',
    # la version du code
    version=imagebelt.imagebelt.__version__,

    packages=find_packages(),

    author="Nicolas Rouviere",
    author_email="infozesk@gmail.com",
    description="An image tool suite",
    long_description=open('README.md').read(),

    install_requires=['Pillow==4.0.0', ],

    # Active la prise en compte du fichier MANIFEST.in
    include_package_data=True,

    #
    url='http://github.com/zesk06/imagebelt',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers.
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Multimedia :: Graphics",
    ],


    #
    #
    entry_points={
        'console_scripts': [
            'imagebelt = imagebelt.imagebelt:main',
        ],
    },
)
