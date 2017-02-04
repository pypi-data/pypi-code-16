# -*- coding:utf-8 -*-

from setuptools import setup
from setuptools import find_packages

VERSION = '0.1.1'

setup(
    name='pyguishudi',
    description='find the operator by phone',
    long_description='',
    classifiers=[],
    keywords='',
    author='Lawes',
    author_email='haiou_chen@sina.cn',
    url='https://github.com/MrLawes/pyguishudi',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'pyguishudi=pyguishudi.guishudi:main',
        ],
    },
)