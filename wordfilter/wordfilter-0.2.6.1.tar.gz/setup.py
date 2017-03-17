#!/usr/bin/env python
from setuptools import setup

try:
    readme = open('README.rst', 'r').read()
except IOError:
    readme = ''

with open('lib/wordfilter/__init__.py') as i:
    version = next(r for r in i.readlines() if '__version__' in r).split('=')[1].strip('"\' \n')

setup(
    name='wordfilter',

    version=version,

    description="A small module meant for use in text generators that lets you filter strings for bad words.",

    long_description=readme,

    author='Neil Freeman & Jim Witschey, based on work by Darius Kazemi',

    author_email='darius.kazemi@gmail.com',

    url='http://tinysubversions.com',

    license='MIT',

    package_dir={'wordfilter': 'lib/wordfilter'},

    packages=['wordfilter'],

    zip_safe=False,

    package_data={
        'wordfilter': ['../badwords.json']
    },

    test_suite='test',

    use_2to3=True,

    classifiers=[
        "Programming Language :: Python",
    ],
)
