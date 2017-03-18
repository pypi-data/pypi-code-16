# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='Bauzak',
    packages=['bauzak'],
    version='0.1.0',
    description='PLC工具',
    long_description='PLC工具',
    author='薛丞宏',
    author_email='ihcaoe@gmail.com',
    url='https://xn--v0qr21b.xn--kpry57d/',
    download_url='https://github.com/i3thuan5/Bauzak',
    keywords=[
        'PLC',
        'TDD',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        'fatek-fbs-lib',
    ],
)
