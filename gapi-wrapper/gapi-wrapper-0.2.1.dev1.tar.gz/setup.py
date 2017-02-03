# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with codecs.open('requirements.txt', 'r', 'utf-8') as f:
    requirements = [x.strip() for x in f.read().splitlines() if x.strip()]

setup(
    name='gapi-wrapper',
    version='0.2.1.dev1',
    description='Wrapper to Google API',
    long_description=long_description,
    author='Suguby',
    author_email='suguby@gmail.com',
    url='https://bitbucket.org/suguby/gapi-wrapper',
    license='MIT',
    packages=find_packages(exclude=['tests.*', 'tests', ]),
    data_files=[('.', ['requirements.txt', 'README.rst'], ), ],
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='google api adwords analytics',
)
