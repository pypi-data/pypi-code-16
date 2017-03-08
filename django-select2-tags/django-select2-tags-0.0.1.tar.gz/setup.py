#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


version = "0.0.1"

setup_kwargs = {}

try:
    setup_kwargs['long_description'] = open('README.rst').read()
except IOError:
    # Use the create_readme_rst command to convert README to reStructuredText
    pass

setup(
    name='django-select2-tags',
    version=version,
    description='Django forms that support new items entered using Select2 with tags enabled',
    author='Jessamyn Smith',
    author_email='jessamyn.smith.com',
    url='https://github.com/jessamynsmith/django-select2-tags',
    download_url='https://github.com/jessamynsmith/django-select2-tags/archive/0.1.tar.gz',
    packages=find_packages(),
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    **setup_kwargs)
