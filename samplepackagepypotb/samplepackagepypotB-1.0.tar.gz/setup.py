#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import samplepackagepypotB

setup(

    name='samplepackagepypotB',

    install_requires = ['samplepackagepypotA > 0.1'],

    # la version du code
    version=samplepackagepypotB.__version__,

    packages=find_packages(),

    # votre pti nom
    author="",


    author_email="",

    # Une description courte
    description="",

    long_description="",

    include_package_data=True,


    # Il est d'usage de mettre quelques metadata à propos de sa lib
    # Pour que les robots puissent facilement la classer.
    # La liste des marqueurs autorisées est longue:
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers.
    #
    # Il n'y a pas vraiment de règle pour le contenu. Chacun fait un peu
    # comme il le sent. Il y en a qui ne mettent rien.
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Communications",
    ],


    entry_points = {},


    license="WTFPL",


)
