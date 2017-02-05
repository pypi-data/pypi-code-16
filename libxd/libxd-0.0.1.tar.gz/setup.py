# -*- coding: utf-8 -*-
#
# Created by libxd on 2016-12-28
#
"""
setup file of setuptools
"""
import codecs
from setuptools import find_packages, setup


def readme():
    """
    render long description for setup function
    """
    with codecs.open('README.md', encoding='UTF-8') as handle:
        return handle.read()


def get_requirements():
    """
    get requirements from requirements.txt
    """
    with open('requirements.txt') as handle:
        return [line.rstrip() for line in handle]

setup(
    name='libxd',
    version='0.0.1',
    description='Personal Python package for some useful functions',
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='libxd',
    url='https://github.com/libxd/libxd.git',
    author='libxd',
    author_email='lihsing@hotmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=get_requirements(),
    entry_points="""
    [console_scripts]
    """,
    include_package_data=True,
    zip_safe=False,
)
