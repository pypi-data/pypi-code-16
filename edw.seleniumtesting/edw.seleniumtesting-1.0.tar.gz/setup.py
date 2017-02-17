# -*- coding: utf-8 -*-
"""Installer for the edw.seleniumtesting package."""

from setuptools import find_packages
from setuptools import setup


LONG_DESCRIPTION = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


VERSION = '1.0'


setup(
    name='edw.seleniumtesting',
    version=VERSION,
    description="Selenium testing metapackage",
    long_description=LONG_DESCRIPTION,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='David Bătrânu',
    author_email='david.batranu@eaudeweb.ro',
    url='https://pypi.python.org/pypi/edw.seleniumtesting',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['edw'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'selenium>=3.0.2',
    ],
    entry_points={
        'console_scripts': ['seleniumtesting = edw.seleniumtesting.main:run_cli'],
        'edw.seleniumtesting': [
            'edw.seleniumtesting.sample = edw.seleniumtesting.sample:suite'
        ]
    }
)
