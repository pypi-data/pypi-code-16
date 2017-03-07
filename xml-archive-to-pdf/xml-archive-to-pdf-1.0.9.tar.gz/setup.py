#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

with open('README.rst') as readme:
    long_description = readme.read()

with open('requirements.txt') as requirements:
    lines = requirements.readlines()
    libraries = [lib for lib in lines if not lib.startswith('-')]
    dependency_links = [link.split()[1] for link in lines if
                        link.startswith('-f')]

setup(
    name='xml-archive-to-pdf',
    version='1.0.9',
    author='di-dip-unistra',
    author_email='di-dip@unistra.fr',
    maintainer='di-dip-unistra',
    maintainer_email='di-dip@unistra.fr',
    url='https://github.com/unistra/xml-archive-to-pdf',
    license='PSF',
    description="Transformation d'un fichier xml de type unistra:archive en fichier pdf",
    long_description=long_description,
    packages=find_packages(),
    download_url='https://github.com/unistra/xml-archive-to-pdf',
    install_requires=libraries,
    dependency_links=dependency_links,
    keywords=[],
    entry_points={
        'console_scripts': [
            'xml-archive-to-pdf = xml_archive_to_pdf.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4"
    ]
)
