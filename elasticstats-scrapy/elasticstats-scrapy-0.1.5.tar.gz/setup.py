#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

requirements = [
    "elasticsearch==5.1.0"
]


setup(
    name='elasticstats-scrapy',
    version='0.1.5',
    description="A scrapy extension to send crawl stats to elasticsearch index.",
    author="Suraj Arya",
    author_email='suraj@loanzen.in',
    url='https://github.com/suraj-arya/elasticstats-scrapy',
    packages=[
        'elasticstats',
    ],
    package_dir={'elasticstats':
                 'elasticstats'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    keywords='elasticstats',
)
