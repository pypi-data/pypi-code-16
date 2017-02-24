##!/usr/bin/env python

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='the_guardian',
    version='0.4',
    author="Aman Abhishek Tiwari",
    author_email="aman.iitk072@gmail.com",
    description="A python guardian which will take "
    "care that you don't waste time.",
    keywords="utilities",
    url="https://github.com/amanabt/the-guardian",
    packages=['the_guardian'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        #"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.5",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Environment :: Console"
    ],
    install_requires=[
    ],

    entry_points={
        'console_scripts': [
            'the_guardian = the_guardian.__main__:main'
        ]
    },
    scripts=["the-guardian"],
    )