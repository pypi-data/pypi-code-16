# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-09-30 14:01:47
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-12-07 12:46:28


from distutils.core import setup
from setuptools import find_packages

setup(
    name='digPhoneExtractor',
    version='0.3.7',
    description='digPhoneExtractor',
    author='Lingzhe Teng',
    author_email='zwein27@gmail.com',
    url='https://github.com/ZwEin27/dig-phone-extractor',
    download_url='https://github.com/ZwEin27/dig-phone-extractor',
    packages=find_packages(),
    keywords=['phone_number', 'extractor'],
    install_requires=['phonenumbers', 'digSparkUtil', 'decorator',
                      'digExtractor', 'requests', 'requests-file',
                      'jsonpath-rw', 'nose2', 'ply', 'six']
)
