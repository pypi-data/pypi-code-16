#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup

__version__ = '0.3.11'

setup(
    name='PyZog',

    packages=['PyZog'],

    version=__version__,

    license='GPL-2.0',

    description='A simple Twitter Client made with python',

    author='LaBatata (Victor Hugo Gomes)',

    author_email='labatata101@gmail.com',

    url='https://github.com/LaBatata101/PyBird',

    download_url=
    'https://github.com/LaBatata101/PyZog/archive/' + __version__ + '.tar.gz',

    keywords=['twitter', 'client', 'twitter client', 'python'],

    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',

        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],

    install_requires=['twython>=3.4.0', 'easygui>=0.98.1'],

    entry_points={
        'console_scripts': ['twitter=PyZog.pyzog:main',],
    },
)
