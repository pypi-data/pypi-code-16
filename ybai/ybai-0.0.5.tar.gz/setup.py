#!/usr/bin/env python3
# coding: utf-8

import re

from setuptools import find_packages, setup

with open('ybai/__init__.py', encoding='utf-8') as fp:
    version = re.search(r"__version__\s*=\s*'([\w\-.]+)'", fp.read()).group(1)

with open('README.md', encoding='utf-8') as fp:
    readme = fp.read()

setup(
    name='ybai',
    version=version,
    packages=find_packages(),
    package_data={
        '': ['*.md'],
    },
    include_package_data=True,
    entry_points={
            'console_scripts': [
                'ybai = ybai.ybai:man'
            ]
        },
    install_requires=[
        'requests',
    ],
    url='https://github.com/mengzhu716/ybai',
    license='MIT',
    author='Yinbing',
    author_email='380711712@qq.com',
    description='个人测试AI',
    long_description=readme,
    keywords=[
        'AI',
        'WeChat',
        'API'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Communications :: Chat',
        'Topic :: Utilities',
    ]
)
