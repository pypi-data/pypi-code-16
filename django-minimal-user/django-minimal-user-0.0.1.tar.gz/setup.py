#!/usr/bin/env python
from setuptools import setup, find_packages
from src.minimal_user import __version__


with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='django-minimal-user',
    version=__version__,
    description='Bare minimum user model for Django',
    long_description=readme,
    author='Ionata Digital',
    author_email='webmaster@ionata.com.au',
    url='https://github.com/ionata/django-minimal-user',
    packages=find_packages('src'),
    install_requires=['django>=1.8.0'],
    package_dir={'': 'src'},
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
