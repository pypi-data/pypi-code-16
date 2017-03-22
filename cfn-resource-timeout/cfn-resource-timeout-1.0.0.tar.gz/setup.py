# -*- coding:utf-8 -*-
from __future__ import absolute_import

import codecs
from setuptools import setup

with codecs.open('README.rst') as readme_file:
    readme = readme_file.read()

with codecs.open('HISTORY.rst') as history_file:
    history = history_file.read()


setup(
    name='cfn-resource-timeout',
    version='1.0.0',
    description=(
        'Wrapper decorators for building CloudFormation custom resources'
    ),
    long_description=readme + '\n\n' + history,
    url='https://github.com/timeoutdigital/cfn-resource-timeout',
    author='Ryan Scott Brown',
    author_email='sb@ryansb.com',
    maintainer='Adam Johnson',
    maintainer_email='adamjohnson@timeout.com',
    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='cloudformation aws cloud custom resource amazon',
    py_modules=["cfn_resource"],
    install_requires=[],
    package_data={},
    data_files=[],
    entry_points={},
)
