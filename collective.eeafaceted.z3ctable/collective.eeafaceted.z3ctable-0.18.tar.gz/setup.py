# -*- coding: utf-8 -*-
"""Installer for the collective.eeafaceted.z3ctable package."""

from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = \
    read('README.rst') + \
    read('CHANGES.rst') + \
    read('docs', 'CONTRIBUTORS.rst') + \
    read('docs', 'LICENSE.rst')

setup(
    name='collective.eeafaceted.z3ctable',
    version='0.18',
    description="Package proposant un type de colonne compatible avec eea.facetednavigation",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Python Zope Plone',
    author='IMIO',
    author_email='dev@imio.be',
    url='http://pypi.python.org/pypi/collective.eeafaceted.z3ctable',
    license='GPL V2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.eeafaceted'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Plone',
        'eea.facetednavigation',
        'plone.api>=1.3.0',
        'setuptools',
        'z3c.table',
    ],
    extras_require={
        'test': [
            'plone.app.dexterity',
            'plone.app.testing',
            'plone.app.relationfield',
            'plone.app.robotframework',
        ],
        'develop': [
            'zest.releaser',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
