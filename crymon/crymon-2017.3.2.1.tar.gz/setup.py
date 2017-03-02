#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, Extension

setup(
    name='crymon',
    version='2017.3.2.1',
    description='Routines for crystallography with single crystals',
    author='Vadim Dyadkin',
    author_email='dyadkin@gmail.com',
    url='https://hg.3lp.cx/crymon',
    license='GPLv3',
    install_requires=[
        'cryio',
    ],
    package_dir={'crymon': ''},
    py_modules=[
        'crymon.__init__',
        'crymon.reconstruct'
    ],
    ext_modules=[
        Extension(
            'crymon._crymon', [
                'src/crymonmodule.c',
                'src/ccp4.c',
            ],
            extra_compile_args=['-O3'],
        )
    ],
    include_package_data=True,
)
