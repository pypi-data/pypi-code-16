# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-09-30 14:01:47
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-10-06 22:44:15


from distutils.core import setup
from setuptools import find_packages

setup(
    name='digPostingDateExtractor',
    version='0.3.1',
    description='digPostingDateExtractor',
    author='Lingzhe Teng',
    author_email='zwein27@gmail.com',
    url='https://github.com/usc-isi-i2/dig-posting-date-extractor',
    download_url='https://github.com/usc-isi-i2/dig-posting-date-extractor',
    packages=find_packages(),
    keywords=['posting', 'date', 'extractor'],
    install_requires=['digExtractor']
)
