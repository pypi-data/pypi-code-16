#! /usr/bin/env python
#! -*- coding: utf-8 -*-

import sys
from setuptools import setup

if __name__ == "__main__":
    setup(
        name = 'keep',
        packages = ['keep', 'keep.commands'],
        version = 1.2,
        description = 'Personal shell command keeper',
        author = 'Himanshu Mishra',
        author_email = 'himanshumishra@iitkgp.ac.in',
        url = "https://github.com/orkohunter/keep",
        download_url = "https://github.com/orkohunter/keep/archive/master.zip",
        include_package_data=True,
        install_requires=[
            'click',
            'request',
            'tabulate'
        ],
        entry_points = {
            'console_scripts': [
                'keep = keep.cli:cli'
            ],
        },
    )

