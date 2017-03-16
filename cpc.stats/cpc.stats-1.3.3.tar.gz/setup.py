#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import find_packages

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

requirements = ['numpy', 'scipy']

setup(
    name="cpc.stats",
    version='v1.3.3',
    description="Set of utilities to perform statistical calculations",
    long_description=readme + '\n\n' + history,
    author="Melissa Ou",
    author_email='melissa.ou@noaa.gov',
    url="https://www.github.com/noaa-nws-cpc/cpc.stats.git",
    packages=find_packages(),
    namespace_packages=['cpc'],
    include_package_data=True,
    install_requires=requirements,
    license="CC",
    zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
    ],
)
