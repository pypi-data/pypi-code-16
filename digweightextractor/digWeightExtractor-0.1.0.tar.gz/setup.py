# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-09-30 14:01:47
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-11-08 18:17:56


from distutils.core import setup
from setuptools import find_packages

setup(
    name='digWeightExtractor',
    version='0.1.0',
    description='digWeightExtractor',
    author='Amandeep Singh',
    author_email='amandeep.s.saggu@gmail.com',
    url='https://github.com/usc-isi-i2/dig-weight-extractor',
    download_url='https://github.com/usc-isi-i2/dig-weight-extractor',
    packages=find_packages(),
    keywords=['weight', 'extractor'],
    install_requires=['digExtractor']
)
